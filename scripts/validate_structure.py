#!/usr/bin/env python3
"""Validate the mandatory total-part-total storyboard structure."""

import argparse
import json
from pathlib import Path


def validate_structure(data):
    errors = []
    structure = data.get("structure")
    if not isinstance(structure, dict):
        return ["missing structure configuration"]
    if structure.get("pattern") != "总-分-总":
        errors.append("structure.pattern must be 总-分-总")
    if structure.get("closing_summary_required") is not True:
        errors.append("structure.closing_summary_required must be true")
    if structure.get("preserve_concept_order") is not True:
        errors.append("structure.preserve_concept_order must be true")
    if structure.get("closing_style") != "concise_summary_then_comment_question":
        errors.append("structure.closing_style must be concise_summary_then_comment_question")
    if structure.get("comment_hook_required") is not True:
        errors.append("structure.comment_hook_required must be true")

    opening = data.get("opening")
    if not isinstance(opening, dict):
        return errors + ["missing opening configuration"]
    concept_records = opening.get("concepts")
    explicit_override = opening.get("explicit_override") is True
    allowed_counts = (1, 2, 3, 4) if explicit_override else (3, 4)
    if not isinstance(concept_records, list) or len(concept_records) not in allowed_counts:
        return errors + [
            "opening.concepts must contain three or four concepts, or one to four "
            "when explicit_override is true"
        ]

    concepts = []
    for index, concept in enumerate(concept_records):
        if not isinstance(concept, dict) or not isinstance(concept.get("display"), str):
            errors.append(f"opening.concepts[{index}].display is missing")
            continue
        display = concept["display"].strip()
        if not display:
            errors.append(f"opening.concepts[{index}].display is empty")
        concepts.append(display)
    if errors or len(concepts) != len(concept_records):
        return errors

    shots = data.get("shots")
    if not isinstance(shots, list) or len(shots) < 3:
        return errors + ["总-分-总 requires at least an opening, an explanation, and a summary shot"]

    first = shots[0]
    if first.get("section") != "opening":
        errors.append("the first shot must use section=opening")
    if first.get("concepts") != concepts:
        errors.append("the opening shot concepts must match opening.concepts in order")

    explained = []
    for shot in shots[1:-1]:
        if shot.get("section") == "explanation":
            shot_concepts = shot.get("concepts", [])
            if isinstance(shot_concepts, list):
                explained.extend(shot_concepts)
    missing = [concept for concept in concepts if concept not in explained]
    if missing:
        errors.append("middle explanation shots do not cover: " + ", ".join(missing))

    final = shots[-1]
    if final.get("section") != "summary":
        errors.append("the final shot must use section=summary")
    if final.get("summary_concepts") != concepts:
        errors.append("the final summary concepts must match the opening count and order")
    summary_text = final.get("summary_text")
    if not isinstance(summary_text, str) or not summary_text.strip():
        errors.append("the final summary must contain one concise summary_text")
    comment_hook = final.get("comment_hook")
    if not isinstance(comment_hook, str) or not comment_hook.strip():
        errors.append("the final summary must end with a comment_hook")
    milestones = final.get("required_milestones", [])
    if "all_summary_concepts_visible" not in milestones:
        errors.append("the final summary must require all_summary_concepts_visible")
    if "comment_hook_visible" not in milestones:
        errors.append("the final summary must require comment_hook_visible")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    args = parser.parse_args()
    data = json.loads(args.config.resolve().read_text(encoding="utf-8"))
    errors = validate_structure(data)
    print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
