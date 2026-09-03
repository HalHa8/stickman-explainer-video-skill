#!/usr/bin/env python3
"""Apply one tempo and gain profile to all narration without trimming tails."""

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def atempo_filters(value):
    if value <= 0:
        raise ValueError("tempo must be positive")
    factors = []
    while value > 2.0:
        factors.append(2.0)
        value /= 2.0
    while value < 0.5:
        factors.append(0.5)
        value /= 0.5
    factors.append(value)
    return [f"atempo={factor:.8g}" for factor in factors]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("--ffmpeg", default="ffmpeg")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    root = config_path.parent / data.get("output_dir", ".")
    source = root.resolve() / "audio" / "raw"
    output = root.resolve() / "audio" / "processed"
    output.mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which(args.ffmpeg) or args.ffmpeg

    audio = data["audio"]
    filters = atempo_filters(float(audio.get("tempo", 1.0)))
    gain = float(audio.get("gain_db", 0.0))
    if gain:
        filters.append(f"volume={gain:.8g}dB")
    limit = float(audio.get("peak_limit", 0.95))
    filters.append(f"alimiter=limit={limit:.8g}")

    for shot in data.get("shots", []):
        tag = f"{int(shot['id']):02d}"
        input_path = source / f"shot_{tag}.wav"
        output_path = output / f"shot_{tag}.wav"
        if not input_path.exists():
            raise SystemExit(f"Missing narration: {input_path}")
        command = [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(input_path), "-filter:a", ",".join(filters),
            "-ar", "22050", "-ac", "1", str(output_path),
        ]
        subprocess.run(command, check=True)
        print(output_path)


if __name__ == "__main__":
    main()
