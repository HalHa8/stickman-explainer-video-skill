#!/usr/bin/env python3
"""Export spoken_text as plain narration paragraphs in shot order."""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("--output")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    output_root = Path(config.get("output_dir", "."))
    if not output_root.is_absolute():
        output_root = config_path.parent / output_root
    output = Path(args.output).resolve() if args.output else output_root.resolve() / "narration.md"

    sections = []
    for shot in config.get("shots", []):
        shot_id = int(shot["id"])
        spoken_text = str(shot.get("spoken_text", "")).strip()
        if not spoken_text:
            raise SystemExit(f"Shot {shot_id} has no spoken_text")
        sections.append(spoken_text)
    if not sections:
        raise SystemExit("No shots found in config")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
