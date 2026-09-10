#!/usr/bin/env python3
"""Generate per-shot narration with Xiaoxiao, Windows TTS, or MamboTTS."""

import argparse
import importlib.util
import json
import math
import os
import shutil
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import wave
from pathlib import Path


DEFAULT_API_URL = "http://127.0.0.1:9880"
DEFAULT_PROMPT = "大家好，欢迎来到我的频道，今天给大家分享一个有趣的内容"
DEFAULT_CUT_PUNC = "，。？！；：、…,.;?!"
DEFAULT_XIAOXIAO_VOICE = "zh-CN-XiaoxiaoNeural"
DEFAULT_HUIHUI_FALLBACK = "Microsoft Huihui Desktop"


def api_is_ready(api_url):
    try:
        with urllib.request.urlopen(api_url.rstrip("/") + "/control", timeout=2):
            return True
    except urllib.error.HTTPError:
        return True
    except (urllib.error.URLError, TimeoutError):
        return False


def resolve_output_root(config_path, config):
    output = Path(config.get("output_dir", "."))
    if not output.is_absolute():
        output = config_path.parent / output
    return output.resolve()


def resolve_mambotts_home(config_path, audio_config, cli_home):
    mambo_config = audio_config.get("mambo", {})
    values = [cli_home, mambo_config.get("home"), os.environ.get("MAMBOTTS_HOME")]
    for value in values:
        if value:
            candidate = Path(value).expanduser()
            if not candidate.is_absolute():
                candidate = config_path.parent / candidate
            return candidate.resolve()
    for parent in (config_path.parent, *config_path.parents):
        candidate = parent / "tools" / "mambotts" / "app"
        if candidate.is_dir():
            return candidate.resolve()
    raise RuntimeError(
        "MamboTTS home was not found. Set audio.mambo.home, MAMBOTTS_HOME, "
        "or pass --mambotts-home."
    )


def validate_mambotts_home(home):
    required = {
        "runtime": home / "GPT-SoVITS" / "runtime" / "python.exe",
        "api": home / "GPT-SoVITS" / "api.py",
        "sovits": home / "models" / "manbo_e8_s168.pth",
        "gpt": home / "models" / "manbo-e10.ckpt",
        "reference": home / "models" / "refer.wav",
    }
    missing = [f"{label}: {path}" for label, path in required.items() if not path.is_file()]
    if missing:
        raise RuntimeError("Incomplete MamboTTS installation:\n" + "\n".join(missing))
    return required


def start_mambo_engine(home, files, api_url, output_root):
    parsed = urllib.parse.urlparse(api_url)
    if parsed.hostname not in {"127.0.0.1", "localhost"}:
        raise RuntimeError("Automatic engine startup is limited to a local MamboTTS API URL.")
    port = parsed.port or 80
    log_dir = output_root / "qa"
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout_handle = (log_dir / "mambotts_engine.stdout.log").open("w", encoding="utf-8")
    stderr_handle = (log_dir / "mambotts_engine.stderr.log").open("w", encoding="utf-8")
    command = [
        str(files["runtime"]),
        str(files["api"]),
        "-a", "127.0.0.1",
        "-p", str(port),
        "-s", str(files["sovits"]),
        "-g", str(files["gpt"]),
        "-dr", str(files["reference"]),
        "-dt", DEFAULT_PROMPT,
        "-dl", "zh",
    ]
    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    process = subprocess.Popen(
        command,
        cwd=home / "GPT-SoVITS",
        stdout=stdout_handle,
        stderr=stderr_handle,
        creationflags=creationflags,
    )
    process._mambo_log_handles = (stdout_handle, stderr_handle)
    return process


def wait_until_ready(process, api_url, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"MamboTTS engine exited during startup (code {process.returncode}).")
        if api_is_ready(api_url):
            return
        time.sleep(1)
    raise RuntimeError(f"MamboTTS API was not ready within {timeout:.0f} seconds: {api_url}")


def stop_engine(process):
    if process is None:
        return
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    for handle in getattr(process, "_mambo_log_handles", ()):
        handle.close()


def verify_wav(path):
    with wave.open(str(path), "rb") as handle:
        channels = handle.getnchannels()
        width = handle.getsampwidth()
        rate = handle.getframerate()
        count = handle.getnframes()
        payload = handle.readframes(count)
    if width != 2:
        raise RuntimeError(f"Expected 16-bit PCM WAV, got sample width {width}: {path}")
    samples = struct.unpack("<" + "h" * (len(payload) // 2), payload)
    rms = math.sqrt(sum(sample * sample for sample in samples) / max(1, len(samples)))
    duration = count / rate
    if duration < 0.4 or rms < 40:
        raise RuntimeError(
            f"Generated WAV is too short or silent: {path}, duration={duration:.3f}, rms={rms:.1f}"
        )
    return {
        "path": str(path),
        "duration": round(duration, 6),
        "sample_rate": rate,
        "channels": channels,
        "rms": round(rms, 2),
    }


def synthesize_mambo(api_url, text, output, ref_audio, speed, timeout):
    params = urllib.parse.urlencode({
        "text": text,
        "text_language": "zh",
        "speed": float(speed),
        "cut_punc": DEFAULT_CUT_PUNC,
        "refer_wav_path": str(ref_audio),
        "prompt_text": DEFAULT_PROMPT,
        "prompt_language": "zh",
    })
    request = urllib.request.Request(api_url.rstrip("/") + "/?" + params)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        payload = response.read()
    if not payload.startswith(b"RIFF"):
        preview = payload[:200].decode("utf-8", errors="replace")
        raise RuntimeError(f"MamboTTS did not return WAV audio ({content_type}): {preview}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(payload)
    return verify_wav(output)


def generate_default(config_path, voice_override=None):
    if sys.platform != "win32":
        raise RuntimeError("The existing default narrator requires Windows TTS.")
    script = Path(__file__).with_name("generate_narration.ps1")
    command = [
        "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", str(script), "-Config", str(config_path),
    ]
    if voice_override:
        command.extend(["-VoiceOverride", voice_override])
    subprocess.run(command, check=True)
    return {
        "ok": True,
        "narrator_voice": "default",
        "actual_voice": voice_override,
    }


def resolve_ffmpeg():
    found = shutil.which("ffmpeg")
    if found:
        return found
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidate = Path(local_app_data) / "Microsoft" / "WinGet" / "Links" / "ffmpeg.exe"
        if candidate.is_file():
            return str(candidate)
    raise RuntimeError("FFmpeg is required to convert Xiaoxiao audio to WAV")


def resolve_edge_tts_command():
    if importlib.util.find_spec("edge_tts") is not None:
        return [sys.executable, "-m", "edge_tts"]
    candidates = [os.environ.get("EDGE_TTS_PYTHON"), shutil.which("python")]
    checked = set()
    for candidate in candidates:
        if not candidate:
            continue
        executable = str(Path(candidate).resolve())
        if executable in checked:
            continue
        checked.add(executable)
        result = subprocess.run(
            [executable, "-c", "import edge_tts"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            return [executable, "-m", "edge_tts"]
    raise RuntimeError("Python package edge-tts is not installed in an available runtime")


def generate_xiaoxiao(config_path, config):
    audio_config = config.get("audio", {})
    requested_voice = str(audio_config.get("voice", DEFAULT_XIAOXIAO_VOICE)).strip()
    fallback_voice = str(
        audio_config.get("fallback_voice", DEFAULT_HUIHUI_FALLBACK)
    ).strip()
    allow_fallback = audio_config.get("allow_voice_fallback", True) is True
    output_root = resolve_output_root(config_path, config)
    raw_dir = output_root / "audio" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    try:
        edge_tts_command = resolve_edge_tts_command()
        ffmpeg = resolve_ffmpeg()
        reports = []
        for shot in config.get("shots", []):
            text = str(shot.get("spoken_text", "")).strip()
            if not text:
                raise RuntimeError(f"Shot {shot.get('id')} has no spoken_text")
            shot_id = int(shot["id"])
            target = raw_dir / f"shot_{shot_id:02d}.wav"
            media = raw_dir / f"shot_{shot_id:02d}.xiaoxiao.mp3"
            if media.exists():
                media.unlink()
            subprocess.run([
                *edge_tts_command,
                "--voice", requested_voice,
                "--rate", str(audio_config.get("xiaoxiao_rate", "+0%")),
                "--text", text,
                "--write-media", str(media),
            ], check=True)
            subprocess.run([
                ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(media), "-ac", "1", "-ar", "24000",
                "-c:a", "pcm_s16le", str(target),
            ], check=True)
            media.unlink(missing_ok=True)
            reports.append(verify_wav(target))
        return {
            "ok": True,
            "narrator_voice": "xiaoxiao",
            "requested_voice": requested_voice,
            "actual_voice": requested_voice,
            "voice_fallback_used": False,
            "files": reports,
        }
    except Exception as exc:
        for media in raw_dir.glob("*.xiaoxiao.mp3"):
            media.unlink(missing_ok=True)
        if not allow_fallback or not fallback_voice:
            raise
        report = generate_default(config_path, fallback_voice)
        report.update({
            "requested_voice": requested_voice,
            "actual_voice": fallback_voice,
            "voice_fallback_used": True,
            "fallback_reason": str(exc),
        })
        return report


def generate_mambo(config_path, config, args):
    audio_config = config.get("audio", {})
    mambo_config = audio_config.get("mambo", {})
    api_url = args.api_url or mambo_config.get("api_url", DEFAULT_API_URL)
    speed = args.speed if args.speed is not None else float(mambo_config.get("speed", 1.0))
    home = resolve_mambotts_home(config_path, audio_config, args.mambotts_home)
    files = validate_mambotts_home(home)
    output_root = resolve_output_root(config_path, config)
    raw_dir = output_root / "audio" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    process = None
    if not api_is_ready(api_url):
        process = start_mambo_engine(home, files, api_url, output_root)
        wait_until_ready(process, api_url, args.startup_timeout)
    reports = []
    try:
        for shot in config.get("shots", []):
            text = str(shot.get("spoken_text", "")).strip()
            if not text:
                raise RuntimeError(f"Shot {shot.get('id')} has no spoken_text")
            target = raw_dir / f"shot_{int(shot['id']):02d}.wav"
            reports.append(synthesize_mambo(
                api_url, text, target, files["reference"], speed, args.request_timeout
            ))
    finally:
        if process is not None and not args.keep_engine_running:
            stop_engine(process)
    return {
        "ok": True,
        "narrator_voice": "mambo",
        "api_url": api_url,
        "engine_started": process is not None,
        "files": reports,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("--narrator-voice", choices=("xiaoxiao", "default", "mambo"))
    parser.add_argument("--mambotts-home")
    parser.add_argument("--api-url")
    parser.add_argument("--speed", type=float)
    parser.add_argument("--startup-timeout", type=float, default=180.0)
    parser.add_argument("--request-timeout", type=float, default=180.0)
    parser.add_argument("--keep-engine-running", action="store_true")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    narrator_voice = args.narrator_voice or config.get("audio", {}).get("narrator_voice", "xiaoxiao")
    if narrator_voice == "xiaoxiao":
        report = generate_xiaoxiao(config_path, config)
    elif narrator_voice == "default":
        report = generate_default(config_path)
    elif narrator_voice == "mambo":
        report = generate_mambo(config_path, config, args)
    else:
        raise SystemExit(f"Unsupported audio.narrator_voice: {narrator_voice}")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
