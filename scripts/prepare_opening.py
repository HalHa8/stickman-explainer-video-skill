#!/usr/bin/env python3
"""Create the standard life-mapping opening, preserving explicit overrides."""

import argparse
import json
from pathlib import Path


DEFAULT_NARRATION_TEMPLATE = "如果把AI放到{domain}，{concepts}，其实一下就能听懂。"
DEFAULT_TITLE_TEMPLATE = "如果把AI放到{domain}？"
LIFE_NARRATION_TEMPLATE = (
    "你每天{familiar_behavior}，其实已经理解了{ai_topic}。"
    "只需要{time_promise}，我用{life_example}告诉你什么是{ai_topic}。"
)
LIFE_TITLE_TEMPLATE = "你每天{familiar_behavior}"
DEFAULT_CUES = {
    1: (0.48,),
    2: (0.38, 0.55),
    3: (0.31, 0.45, 0.59),
    4: (0.28, 0.39, 0.49, 0.59),
}
LIFE_CUES = {
    1: (0.58,),
    2: (0.52, 0.68),
    3: (0.47, 0.60, 0.73),
    4: (0.43, 0.54, 0.65, 0.76),
}


def require_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"Missing required opening field: {field}")
    return value.strip()


def join_concepts(concepts):
    if len(concepts) == 1:
        return concepts[0]
    return "、".join(concepts[:-1]) + "和" + concepts[-1]


def format_template(template, domain, concepts, field, extra_values=None):
    values = {"domain": domain, "concepts": join_concepts(concepts)}
    values.update({f"concept_{index + 1}": value for index, value in enumerate(concepts)})
    if extra_values:
        values.update(extra_values)
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

    concepts = opening.get("concepts")
    explicit_override = opening.get("explicit_override") is True
    life_mapping = opening.get("hook_style") == "life_mapping" and not explicit_override
    if life_mapping:
        domain_spoken = str(opening.get("domain_spoken", "")).strip()
        domain_display = str(opening.get("domain_display", "")).strip()
    else:
        domain_spoken = require_text(opening.get("domain_spoken"), "domain_spoken")
        domain_display = require_text(opening.get("domain_display"), "domain_display")
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

    extra_spoken = {}
    extra_display = {}
    concept_mappings = []
    if life_mapping:
        familiar_behavior_spoken = require_text(
            opening.get("familiar_behavior_spoken"), "familiar_behavior_spoken"
        )
        familiar_behavior_display = require_text(
            opening.get("familiar_behavior_display"), "familiar_behavior_display"
        )
        life_example_spoken = require_text(
            opening.get("life_example_spoken"), "life_example_spoken"
        )
        life_example_display = require_text(
            opening.get("life_example_display"), "life_example_display"
        )
        time_promise_spoken = require_text(
            opening.get("time_promise_spoken", "60秒"), "time_promise_spoken"
        )
        time_promise_display = require_text(
            opening.get("time_promise_display", "60秒"), "time_promise_display"
        )
        ai_topic_spoken = str(opening.get("ai_topic_spoken", "")).strip() or join_concepts(
            spoken_concepts
        )
        ai_topic_display = str(opening.get("ai_topic_display", "")).strip() or join_concepts(
            display_concepts
        )
        concept_mappings = opening.get("concept_mappings")
        if not isinstance(concept_mappings, list) or len(concept_mappings) != len(display_concepts):
            raise SystemExit("opening.concept_mappings must contain one record per opening concept")
        life_elements = []
        for index, (mapping, concept) in enumerate(zip(concept_mappings, display_concepts)):
            if not isinstance(mapping, dict):
                raise SystemExit(f"opening.concept_mappings[{index}] must be an object")
            mapped_concept = require_text(
                mapping.get("concept"), f"concept_mappings[{index}].concept"
            )
            if mapped_concept != concept:
                raise SystemExit(
                    f"concept_mappings[{index}].concept must match opening concept {concept}"
                )
            require_text(mapping.get("core_role"), f"concept_mappings[{index}].core_role")
            life_elements.append(
                require_text(mapping.get("life_element"), f"concept_mappings[{index}].life_element")
            )
        if len(set(life_elements)) != len(life_elements):
            raise SystemExit("concept_mappings life_element values must be distinct")
        extra_spoken = {
            "familiar_behavior": familiar_behavior_spoken,
            "life_example": life_example_spoken,
            "time_promise": time_promise_spoken,
            "ai_topic": ai_topic_spoken,
        }
        extra_display = {
            "familiar_behavior": familiar_behavior_display,
            "life_example": life_example_display,
            "time_promise": time_promise_display,
            "ai_topic": ai_topic_display,
        }

    narration_template = require_text(
        opening.get(
            "narration_template",
            LIFE_NARRATION_TEMPLATE if life_mapping else DEFAULT_NARRATION_TEMPLATE,
        ),
        "narration_template",
    )
    title_template = require_text(
        opening.get("title_template", LIFE_TITLE_TEMPLATE if life_mapping else DEFAULT_TITLE_TEMPLATE),
        "title_template",
    )

    shot = {
        "id": 1,
        "section": "opening",
        "spoken_text": format_template(
            narration_template,
            domain_spoken,
            spoken_concepts,
            "narration_template",
            extra_spoken,
        ),
        "title_text": format_template(
            title_template,
            domain_display,
            display_concepts,
            "title_template",
            extra_display,
        ),
        "concepts": display_concepts,
        "display_text": [
            {"text": concept, "cue": cue}
            for concept, cue in zip(
                display_concepts,
                (LIFE_CUES if life_mapping else DEFAULT_CUES)[len(display_concepts)],
            )
        ],
        "required_milestones": (
            [
                "familiar_scene_visible_in_first_second",
                "recognition_contrast_visible",
                "time_commitment_visible",
                *[f"concept_{index}_visible" for index in range(1, len(display_concepts) + 1)],
                "all_concept_chips_visible",
            ]
            if life_mapping
            else [
                "opening_question_visible",
                *[f"concept_{index}_visible" for index in range(1, len(display_concepts) + 1)],
                "all_concept_chips_visible",
            ]
        ),
    }
    if life_mapping:
        shot.update(
            {
                "hook_style": "life_mapping",
                "familiar_behavior": extra_display["familiar_behavior"],
                "life_example": extra_display["life_example"],
                "time_promise": extra_display["time_promise"],
                "ai_topic": extra_display["ai_topic"],
                "concept_mappings": concept_mappings,
            }
        )

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
