#!/usr/bin/env python3
"""Validate metadata, full decode, subtitles, platform-safe zones, and shot pauses."""

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path

from validate_structure import validate_structure


def run(command):
    return subprocess.run(
        command, check=True, text=True, encoding="utf-8", errors="replace", capture_output=True
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video")
    parser.add_argument("config")
    parser.add_argument("--timing")
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")
    parser.add_argument("--pause-tolerance", type=float, default=0.12)
    args = parser.parse_args()

    video = Path(args.video).resolve()
    config_path = Path(args.config).resolve()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    ffmpeg = shutil.which(args.ffmpeg) or args.ffmpeg
    ffprobe = shutil.which(args.ffprobe) or args.ffprobe
    errors, warnings = validate_structure(data), []

    probe = run([
        ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)
    ])
    metadata = json.loads(probe.stdout)
    streams = metadata.get("streams", [])
    video_streams = [stream for stream in streams if stream.get("codec_type") == "video"]
    audio_streams = [stream for stream in streams if stream.get("codec_type") == "audio"]
    subtitle_streams = [stream for stream in streams if stream.get("codec_type") == "subtitle"]
    if not video_streams:
        errors.append("missing video stream")
    else:
        stream = video_streams[0]
        expected = data["video"]
        if int(stream.get("width", 0)) < int(expected["width"]) or int(stream.get("height", 0)) < int(expected["height"]):
            errors.append(f"resolution is {stream.get('width')}x{stream.get('height')}, expected at least {expected['width']}x{expected['height']}")
        fps = float(Fraction(stream.get("avg_frame_rate", "0/1")))
        if fps + 0.001 < float(expected["fps"]):
            errors.append(f"frame rate is {fps:.3f}, expected at least {expected['fps']}")
    if not audio_streams:
        errors.append("missing audio stream")
    if not data.get("subtitles", False) and subtitle_streams:
        errors.append("subtitle stream exists while subtitles are disabled")

    decode = subprocess.run(
        [ffmpeg, "-v", "error", "-i", str(video), "-f", "null", "-"],
        text=True, encoding="utf-8", errors="replace", capture_output=True,
    )
    if decode.returncode:
        errors.append("full decode failed: " + decode.stderr.strip()[-500:])

    timing_path = Path(args.timing).resolve() if args.timing else (config_path.parent / data.get("output_dir", ".") / "qa" / "timing.json").resolve()
    measured_pauses = []
    if timing_path.exists():
        timing = json.loads(timing_path.read_text(encoding="utf-8"))
        silence = subprocess.run([
            ffmpeg, "-hide_banner", "-i", str(video),
            "-af", "silencedetect=noise=-38dB:d=0.5", "-f", "null", "-"
        ], text=True, encoding="utf-8", errors="replace", capture_output=True)
        intervals = []
        starts = [float(value) for value in re.findall(r"silence_start: ([0-9.]+)", silence.stderr)]
        ends = [float(value) for value in re.findall(r"silence_end: ([0-9.]+)", silence.stderr)]
        for start, end in zip(starts, ends):
            intervals.append((start, end))
        boundary = 0.0
        target = float(data["audio"].get("inter_shot_pause", 1.0))
        for shot in timing.get("shots", [])[:-1]:
            boundary += float(shot["video_duration"])
            match = next(((start, end) for start, end in intervals if start - 0.08 <= boundary <= end + 0.08), None)
            if not match:
                errors.append(f"no silence interval found at shot boundary {boundary:.3f}s")
                continue
            duration = match[1] - match[0]
            measured_pauses.append(round(duration, 6))
            if abs(duration - target) > args.pause_tolerance:
                errors.append(f"pause {duration:.3f}s at {boundary:.3f}s is outside {target:.3f}±{args.pause_tolerance:.3f}s")

    safe_area_checked = False
    try:
        from PIL import Image
        expected = data["video"]
        top_ratio = float(expected.get("safe_area_top", 0.0))
        right_ratio = float(expected.get("safe_area_right", 0.20))
        bottom_ratio = float(expected.get("safe_area_bottom", 0.20))
        if any((top_ratio, right_ratio, bottom_ratio)) and video_streams:
            duration = float(metadata.get("format", {}).get("duration", 0.0))
            background = expected.get("background", "#FFFFFF").lstrip("#")
            target_rgb = tuple(int(background[index:index + 2], 16) for index in (0, 2, 4))
            with tempfile.TemporaryDirectory() as temp:
                for index, timestamp in enumerate((duration * 0.1, duration * 0.5, duration * 0.9)):
                    frame = Path(temp) / f"frame_{index}.png"
                    run([ffmpeg, "-v", "error", "-ss", f"{timestamp:.3f}", "-i", str(video), "-frames:v", "1", str(frame)])
                    image = Image.open(frame).convert("RGB")
                    regions = {
                        "top": (0, 0, image.width, int(image.height * top_ratio)),
                        "right": (int(image.width * (1 - right_ratio)), 0, image.width, image.height),
                        "bottom": (0, int(image.height * (1 - bottom_ratio)), image.width, image.height),
                    }
                    for name, box in regions.items():
                        if box[2] <= box[0] or box[3] <= box[1]:
                            continue
                        region = image.crop(box)
                        pixel_source = (
                            region.get_flattened_data()
                            if hasattr(region, "get_flattened_data")
                            else region.getdata()
                        )
                        pixels = list(pixel_source)
                        matching = sum(
                            all(abs(pixel[channel] - target_rgb[channel]) <= 12 for channel in range(3))
                            for pixel in pixels
                        )
                        if matching / max(1, len(pixels)) < 0.995:
                            errors.append(f"{name} safe area is not clear at {timestamp:.3f}s")
                safe_area_checked = True
    except (ImportError, subprocess.CalledProcessError, OSError, ValueError) as exc:
        warnings.append(f"safe-area pixel check skipped: {exc}")

    report = {
        "video": str(video),
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "measured_pauses": measured_pauses,
        "safe_area_checked": safe_area_checked,
        "metadata": metadata,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
