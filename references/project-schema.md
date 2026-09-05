# Project configuration

Store the project configuration as UTF-8 JSON. Paths are relative to the configuration file unless absolute. Keep outputs inside the current project directory.

```json
{
  "project_name": "agent-basketball",
  "output_dir": ".",
  "video": {
    "width": 1440,
    "height": 2560,
    "fps": 45,
    "safe_area_top": 0.1,
    "background": "#FFFFFF"
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
    "silence_threshold_db": -45.0
  },
  "subtitles": false,
  "structure": {
    "pattern": "总-分-总",
    "closing_summary_required": true,
    "preserve_concept_order": true,
    "closing_style": "concise_summary_then_comment_question",
    "comment_hook_required": true
  },
  "opening": {
    "required": true,
    "explicit_override": false,
    "hook_style": "life_mapping",
    "familiar_behavior_spoken": "打篮球",
    "familiar_behavior_display": "打篮球",
    "life_example_spoken": "一场篮球比赛",
    "life_example_display": "一场篮球比赛",
    "time_promise_spoken": "60秒",
    "time_promise_display": "60秒",
    "ai_topic_spoken": "Agent、Tool、Skill和MultiAgent",
    "ai_topic_display": "Agent、Tool、Skill和Multi-agent",
    "domain_spoken": "篮球场",
    "domain_display": "篮球场",
    "concepts": [
      {"spoken": "Agent", "display": "Agent"},
      {"spoken": "Tool", "display": "Tool"},
      {"spoken": "Skill", "display": "Skill"},
      {"spoken": "MultiAgent", "display": "Multi-agent"}
    ],
    "concept_mappings": [
      {"concept": "Agent", "core_role": "自主判断并完成任务", "life_element": "持球组织进攻的球员"},
      {"concept": "Tool", "core_role": "提供单一可调用动作", "life_element": "篮球"},
      {"concept": "Skill", "core_role": "组织一组动作形成稳定能力", "life_element": "运球突破"},
      {"concept": "Multi-agent", "core_role": "多个主体协作完成共同目标", "life_element": "整支球队"}
    ],
    "narration_template": "你每天{familiar_behavior}，其实已经理解了{ai_topic}。只需要{time_promise}，我用{life_example}告诉你什么是{ai_topic}。",
    "title_template": "你每天{familiar_behavior}"
  },
  "shots": [
    {
      "id": 1,
      "section": "opening",
      "hook_style": "life_mapping",
      "spoken_text": "你每天打篮球，其实已经理解了Agent、Tool、Skill和MultiAgent。只需要60秒，我用一场篮球比赛告诉你什么是Agent、Tool、Skill和MultiAgent。",
      "title_text": "你每天打篮球",
      "familiar_behavior": "打篮球",
      "life_example": "一场篮球比赛",
      "time_promise": "60秒",
      "ai_topic": "Agent、Tool、Skill和Multi-agent",
      "concepts": ["Agent", "Tool", "Skill", "Multi-agent"],
      "display_text": [
        {"text": "Agent", "cue": 0.43},
        {"text": "Tool", "cue": 0.54},
        {"text": "Skill", "cue": 0.65},
        {"text": "Multi-agent", "cue": 0.76}
      ],
      "required_milestones": [
        "familiar_scene_visible_in_first_second",
        "recognition_contrast_visible",
        "time_commitment_visible",
        "concept_1_visible",
        "concept_2_visible",
        "concept_3_visible",
        "concept_4_visible",
        "all_concept_chips_visible"
      ]
    },
    {
      "id": 2,
      "section": "explanation",
      "concepts": ["Agent", "Tool"],
      "spoken_text": "先分别解释Agent和Tool。",
      "display_text": []
    },
    {
      "id": 3,
      "section": "explanation",
      "concepts": ["Skill", "Multi-agent"],
      "spoken_text": "再分别解释Skill和MultiAgent。",
      "display_text": []
    },
    {
      "id": 4,
      "section": "summary",
      "spoken_text": "所以，Agent负责思考，Tool提供动作，Skill组织动作，MultiAgent完成协作。评论区回复我，你还想用篮球理解哪个AI概念？",
      "summary_text": "所以，Agent负责思考，Tool提供动作，Skill组织动作，MultiAgent完成协作。",
      "comment_hook": "评论区回复我，你还想用篮球理解哪个AI概念？",
      "summary_concepts": ["Agent", "Tool", "Skill", "Multi-agent"],
      "required_milestones": ["all_summary_concepts_visible", "comment_hook_visible"]
    }
  ]
}
```

## Field behavior

- `structure`: declares the mandatory `总-分-总` narrative and the default concise-summary-then-comment-question ending.
- `opening`: the mandatory first-shot source of truth. For the default hook, fill the familiar behavior, life example, time promise, three or four concepts, and one mapping record per concept before running `scripts/prepare_opening.py`.
- `explicit_override`: keep `false` for the standard opening. Set it to `true` only when the user explicitly supplies different opening wording or a different concept count; the helper then accepts one to four concepts.
- `hook_style`: new projects use `life_mapping`. A legacy project without this field keeps its old opening behavior.
- `familiar_behavior_*`: a behavior, object, or situation that can appear visually within the first second.
- `life_example_*`: the familiar system used to carry the explanation.
- `time_promise_*`: a short, credible commitment such as `60秒`.
- `ai_topic_*`: the topic named in both hook sentences. It may be an umbrella topic or a natural list; if omitted, the helper derives it from `concepts`.
- `concept_mappings`: exactly one record per concept, in display order. Each record contains the exact display `concept`, its `core_role`, and a distinct `life_element` so the mapping remains one-to-one.
- `domain_spoken` and each concept's `spoken`: pronunciation-safe TTS forms.
- `domain_display` and each concept's `display`: exact on-screen forms.
- `domain_spoken` and `domain_display` remain for backward compatibility and optional downstream scene metadata; the default life-mapping hook does not require them.
- `narration_template`: supports `{familiar_behavior}`, `{life_example}`, `{time_promise}`, `{ai_topic}`, and `{concepts}`. `{concepts}` expands to a natural Chinese list.
- `narration_template` and `title_template`: standard templates. Change them only when the user explicitly requests a different opening.
- `section`: one of `opening`, `explanation`, `transition`, or `summary`. The first shot is `opening`; the final shot is `summary`.
- `concepts` on middle shots: headline concepts meaningfully explained by that shot. Across all `explanation` shots, cover every opening concept.
- `summary_concepts`: exact display names summarized by the closing shot, in the same order as `opening.concepts`.
- `summary_text`: the single concise concluding statement. Do not duplicate it with a second full recap.
- `comment_hook`: the final topic-specific question inviting viewers to reply in the comments.
- `spoken_text`: exact input for TTS. Remove punctuation that causes unintended pronunciation only here.
- `display_text`: exact screen spelling. Do not silently copy TTS workarounds into it.
- `cue`: normalized progress from 0 to 1 by default. A project may use seconds, but must use one convention consistently.
- `required_milestones`: visual states that must appear even when the shot becomes shorter.
- `inter_shot_pause`: desired silence between the end of one spoken segment and the start of the next, not merely the gap between media files.
- `narrator_voice`: narration backend. Omit it or use `default` to preserve the existing Windows voice workflow. Use `mambo` only when the user explicitly requests the optional local Mambo voice.
- `voice` and `base_rate`: settings for `narrator_voice: "default"`; they remain unchanged when Mambo is selected.
- `audio.mambo` (optional): may contain `home`, `api_url`, and `speed`. `home` points to the MamboTTS app directory; otherwise the narration script checks `MAMBOTTS_HOME` and searches ancestor workspaces for `tools/mambotts/app`. `api_url` defaults to `http://127.0.0.1:9880`; `speed` defaults to `1.0` before shared post-processing tempo is applied.
- `safe_area_top`: fraction of the complete frame that remains free of content.
- `subtitles`: concept graphics do not change this value.

Run `scripts/prepare_opening.py project.json` after filling `opening`. The default life-mapping hook requires three or four concepts and a complete one-to-one mapping. With an explicit user-approved override it accepts one to four concepts and preserves the custom narration template. Use `--force` only when deliberately refreshing an existing first shot.

Run `scripts/validate_structure.py project.json` after the storyboard is complete and again before final delivery. It verifies the opening overview, middle coverage, concise summary, final comment hook, and visual concept continuity.

Run `scripts/export_narration.py project.json` after the final `spoken_text` is settled and before delivery. It writes `narration.md` as plain paragraphs in shot order, separated only by blank lines, with no title, shot number, heading, storyboard, visual, cue, timing, or production fields.

## Suggested artifact layout

```text
project-dir/
|-- project.json
|-- narration.md
|-- storyboard.json
|-- audio/
|   |-- raw/
|   `-- processed/
|-- frames/
|-- shots/
|-- versions/
|-- qa/
`-- latest.mp4
```

Keep only durable deliverables and useful intermediate files. Remove known-invalid partial encodes after confirming their exact path.
