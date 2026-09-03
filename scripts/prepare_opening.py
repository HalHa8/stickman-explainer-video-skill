#!/usr/bin/env python3
"""Create the standard opening shot, preserving explicit user overrides."""

import argparse
import json
from pathlib import Path


DEFAULT_NARRATION_TEMPLATE = "如果把AI放到{domain}，{concepts}，其实一下就能听懂。"
DEFAULT_TITLE_TEMPLATE = "如果把AI放到{domain}？"
DEFAULT_CUES = {
    1: (0.48,),
    2: (0.38, 0.55),
    3: (0.31, 0.45, 0.59),
    4: (0.28, 0.39, 0.49, 0.59),
}


def require_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"Missing required opening field: {field}")
    return value.strip()


def join_concepts(concepts):
    if len(concepts) == 1:
        return concepts[0]
    return "、".join(concepts[:-1]) + "和" + concepts[-1]


def format_template(template, domain, concepts, field):
    values = {"domain": domain, "concepts": join_concepts(concepts)}
    values.update({f"concept_{index + 1}": value for index, value in enumerate(concepts)})
    try:
        return template.format(**values)
    except (KeyError, ValueError) as exc:
        raise SystemExit(f"Invalid {field}: {exc}") from exc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    config_path = args.config.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    opening = config.get("opening")
    if not isinstance(opening, dict):
        raise SystemExit("Missing required opening configuration")
    if opening.get("required") is False:
        raise SystemExit("The standard opening is disabled; use only with an explicit user override")

    domain_spoken = require_text(opening.get("domain_spoken"), "domain_spoken")
    domain_display = require_text(opening.get("domain_display"), "domain_display")
    concepts = opening.get("concepts")
    explicit_override = opening.get("explicit_override") is True
    allowed_counts = (1, 2, 3, 4) if explicit_override else (3, 4)
    if not isinstance(concepts, list) or len(concepts) not in allowed_counts:
        raise SystemExit(
            "opening.concepts must contain three or four concepts, or one to four "
            "when explicit_override is true"
        )

    spoken_concepts = []
    display_concepts = []
    for index, concept in enumerate(concepts, start=1):
        if not isinstance(concept, dict):
            raise SystemExit(f"opening.concepts[{index - 1}] must be an object")
        spoken_concepts.append(require_text(concept.get("spoken"), f"concepts[{index - 1}].spoken"))
        display_concepts.append(require_text(concept.get("display"), f"concepts[{index - 1}].display"))

    narration_template = require_text(
        opening.get("narration_template", DEFAULT_NARRATION_TEMPLATE), "narration_template"
    )
    title_template = require_text(
        opening.get("title_template", DEFAULT_TITLE_TEMPLATE), "title_template"
    )

    shot = {
        "id": 1,
        "section": "opening",
        "spoken_text": format_template(
            narration_template, domain_spoken, spoken_concepts, "narration_template"
        ),
        "title_text": format_template(
            title_template, domain_display, display_concepts, "title_template"
        ),
        "concepts": display_concepts,
        "display_text": [
            {"text": concept, "cue": cue}
            for concept, cue in zip(display_concepts, DEFAULT_CUES[len(display_concepts)])
        ],
        "required_milestones": [
            "opening_question_visible",
            *[f"concept_{index}_visible" for index in range(1, len(display_concepts) + 1)],
            "all_concept_chips_visible",
        ],
    }

    shots = config.setdefault("shots", [])
    existing_index = next(
        (index for index, item in enumerate(shots) if item.get("id") == 1), None
    )
    if existing_index is not None and not args.force:
        raise SystemExit("Shot 1 already exists; pass --force to refresh it")
    if existing_index is None:
        shots.insert(0, shot)
    else:
        shots[existing_index] = shot
        shots.sort(key=lambda item: item.get("id", 0))

    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(config_path)


if __name__ == "__main__":
    main()
