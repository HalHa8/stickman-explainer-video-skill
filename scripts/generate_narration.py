#!/usr/bin/env python3
"""Generate per-shot narration with the existing Windows voice or MamboTTS."""

import argparse
import json
import math
import os
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


def generate_default(config_path):
    if sys.platform != "win32":
        raise RuntimeError("The existing default narrator requires Windows TTS.")
    script = Path(__file__).with_name("generate_narration.ps1")
    subprocess.run([
        "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", str(script), "-Config", str(config_path),
    ], check=True)
    return {"ok": True, "narrator_voice": "default"}


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
    parser.add_argument("--narrator-voice", choices=("default", "mambo"))
    parser.add_argument("--mambotts-home")
    parser.add_argument("--api-url")
    parser.add_argument("--speed", type=float)
    parser.add_argument("--startup-timeout", type=float, default=180.0)
    parser.add_argument("--request-timeout", type=float, default=180.0)
    parser.add_argument("--keep-engine-running", action="store_true")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    narrator_voice = args.narrator_voice or config.get("audio", {}).get("narrator_voice", "default")
    if narrator_voice == "default":
        report = generate_default(config_path)
    elif narrator_voice == "mambo":
        report = generate_mambo(config_path, config, args)
    else:
        raise SystemExit(f"Unsupported audio.narrator_voice: {narrator_voice}")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
