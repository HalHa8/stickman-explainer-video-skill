#!/usr/bin/env python3
"""Create a stickman explainer project with the approved default profile."""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir")
    parser.add_argument("--name")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    root = Path(args.project_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    config_path = root / "project.json"
    if config_path.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing config: {config_path}")

    config = {
        "project_name": args.name or root.name,
        "output_dir": ".",
        "video": {
            "width": 1440,
            "height": 2560,
            "fps": 45,
            "safe_area_top": 0.10,
            "safe_area_right": 0.20,
            "safe_area_bottom": 0.20,
            "background": "#FFFFFF",
        },
        "audio": {
            "narrator_voice": "default",
            "voice": "Microsoft Huihui Desktop",
            "base_rate": 2,
            "tempo": 1.2,
            "inter_shot_pause": 1.0,
            "final_hold": 0.8,
            "gain_db": 4.0,
            "peak_limit": 0.95,
            "silence_threshold_db": -45.0,
        },
        "subtitles": False,
        "structure": {
            "pattern": "总-分-总",
            "closing_summary_required": True,
            "preserve_concept_order": True,
            "closing_style": "concise_summary_then_comment_question",
            "comment_hook_required": True,
        },
        "opening": {
            "required": True,
            "explicit_override": False,
            "hook_style": "life_mapping",
            "hook_type": "pain_point_reframe",
            "familiar_behavior_spoken": "",
            "familiar_behavior_display": "",
            "life_example_spoken": "",
            "life_example_display": "",
            "life_example_scene_spoken": "",
            "life_example_scene_display": "",
            "time_promise_spoken": "60秒",
            "time_promise_display": "60秒",
            "ai_topic_spoken": "",
            "ai_topic_display": "",
            "concept_mappings": [],
            "domain_spoken": "",
            "domain_display": "",
            "concepts": [],
        },
        "shots": [],
    }
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for relative in ("audio/raw", "audio/processed", "frames", "shots", "versions", "qa"):
        (root / relative).mkdir(parents=True, exist_ok=True)
    print(config_path)


if __name__ == "__main__":
    main()
