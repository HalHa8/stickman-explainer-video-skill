#!/usr/bin/env python3
"""Measure speech boundaries without trimming audio and compute shot frames."""

import argparse
import json
import math
import sys
import wave
from array import array
from pathlib import Path


def measure_wav(path, threshold_db=-45.0, window_ms=10):
    with wave.open(str(path), "rb") as handle:
        if handle.getsampwidth() != 2:
            raise ValueError(f"Only 16-bit PCM WAV is supported: {path}")
        rate = handle.getframerate()
        channels = handle.getnchannels()
        frames = handle.getnframes()
        samples = array("h", handle.readframes(frames))
    if sys.byteorder != "little":
        samples.byteswap()
    window = max(channels, int(rate * channels * window_ms / 1000))
    threshold = 32767 * (10 ** (threshold_db / 20))
    active = []
    for start in range(0, len(samples), window):
        chunk = samples[start:start + window]
        if not chunk:
            continue
        rms = math.sqrt(sum(value * value for value in chunk) / len(chunk))
        if rms >= threshold:
            active.append((start, min(len(samples), start + window)))
    duration = frames / rate
    if not active:
        return {"duration": duration, "leading_silence": duration, "trailing_silence": 0.0}
    first_frame = active[0][0] / channels
    last_frame = active[-1][1] / channels
    return {
        "duration": duration,
        "leading_silence": first_frame / rate,
        "trailing_silence": max(0.0, duration - last_frame / rate),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("--audio-dir")
    parser.add_argument("--output")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    root = (config_path.parent / data.get("output_dir", ".")).resolve()
    audio_dir = Path(args.audio_dir).resolve() if args.audio_dir else root / "audio" / "processed"
    output = Path(args.output).resolve() if args.output else root / "qa" / "timing.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    fps = float(data["video"]["fps"])
    audio_config = data["audio"]
    pause = float(audio_config.get("inter_shot_pause", 1.0))
    final_hold = float(audio_config.get("final_hold", 0.8))
    threshold = float(audio_config.get("silence_threshold_db", -45.0))
    minimum_tail = 0.05
    shots = data.get("shots", [])
    measurements = []
    for shot in shots:
        path = audio_dir / f"shot_{int(shot['id']):02d}.wav"
        if not path.exists():
            raise SystemExit(f"Missing processed narration: {path}")
        measurements.append(measure_wav(path, threshold))

    result = {"fps": fps, "target_pause": pause, "shots": []}
    for index, (shot, measured) in enumerate(zip(shots, measurements)):
        if index + 1 < len(shots):
            next_leading = measurements[index + 1]["leading_silence"]
            ideal = measured["duration"] + pause - measured["trailing_silence"] - next_leading
            duration = max(measured["duration"] + minimum_tail, ideal)
            actual_gap = duration - measured["duration"] + measured["trailing_silence"] + next_leading
        else:
            duration = measured["duration"] + final_hold
            actual_gap = None
        frames = math.ceil(duration * fps)
        video_duration = frames / fps
        if actual_gap is not None:
            actual_gap += video_duration - duration
        result["shots"].append({
            "id": int(shot["id"]),
            "audio_duration": round(measured["duration"], 6),
            "leading_silence": round(measured["leading_silence"], 6),
            "trailing_silence": round(measured["trailing_silence"], 6),
            "frame_count": frames,
            "video_duration": round(video_duration, 6),
            "actual_gap_to_next": None if actual_gap is None else round(actual_gap, 6),
        })
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
