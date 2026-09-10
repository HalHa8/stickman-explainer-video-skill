---
name: stickman-explainer-video
description: Create narrated vertical stickman teaching videos from topic selection through concept confirmation, script, storyboard, rendering, and QA. Use automatically when the user asks to generate a 火柴人教学视频, stickman explainer, or similar educational animation. Do not use for static stickman images, photorealistic video, or ordinary editing of unrelated footage.
---

# Stickman Explainer Video

Create a clear, platform-ready teaching video while preserving the user's approved concept model and visual language.

## Required execution mode confirmation

At the start of every new video request, before creating or modifying any production artifact, explicitly confirm which execution mode the user wants:

- **One-click final video:** after the mode is confirmed, continue through concept interpretation, narration, storyboard, pilot rendering when useful, audio generation, full rendering, and QA without asking for intermediate approval.
- **Review as you go:** pause for the user's approval at the concept model, narration and storyboard, and representative pilot-shot stages before continuing to the next production stage.

Production artifacts include polished narration, storyboards, pilot images, generated audio, frames, and video files. Topic exploration and a rough concept proposal may happen before mode selection, but do not start production until the mode is confirmed. If the user explicitly chose a mode in the current request, acknowledge it and do not ask again. Never infer a mode merely because the prompt is detailed.

## Workflow

1. Confirm **One-click final video** or **Review as you go** before production begins.
2. Offer topic ideas only when requested or when the user has not chosen a topic.
3. Draft the core explanation or analogy. In Review as you go mode, obtain confirmation before polished narration. In One-click final video mode, preserve the user's supplied explanation as authoritative and resolve minor gaps without pausing.
4. Select three or four headline AI concepts by default. Before drafting the opening, extract each concept's core role, choose one familiar everyday system, and build a one-to-one mapping between the concepts and distinct elements of that system. Set the editorial intensity: when the user wants short-form virality, preserve approved provocative wording, dramatic equivalence, compressed character arcs, and controversy hooks instead of automatically softening them into academic language. Keep the underlying AI relationships accurate. Use the life-mapping hook below, then design the concept-by-concept middle and a concise closing summary followed by a comment question. Write narration and split it into shots with characters, actions, concept text, visual cues, and required milestones. In Review as you go mode, pause for approval of both before generating media.
5. When visual judgment is still open, render one representative pilot shot before the full video. In Review as you go mode, pause for visual approval; in One-click final video mode, inspect and refine it internally without pausing.
6. Generate every narration segment with the selected `audio.narrator_voice` backend and one base rate. Use Xiaoxiao as the default narrator, falling back to local Huihui only when Xiaoxiao is unavailable and recording that fallback in the project and QA report. Measure the resulting audio before assigning shot durations.
7. Run the structure validator, then render topic-specific scenes, synchronize concept text to the spoken cues, and preserve every required visual milestone.
8. Export `narration.md` from the final `spoken_text` in shot order, using one plain paragraph per shot. Include no title, shot number, heading, storyboard, visual direction, timing, or production note.
9. Build the final video and run deterministic media and structure QA before publishing `latest.mp4`.

Read [storyboard-guidelines.md](references/storyboard-guidelines.md) before drafting narration or shots. Read [project-schema.md](references/project-schema.md) when initializing or building a project. Read [basketball-example.md](references/basketball-example.md) only when a concrete example or the basketball template is useful.

## Life-mapping opening hooks

Unless the user explicitly requests a different opening, every video created with this skill must begin with these two narration sentences:

`你每天{familiar_behavior}，其实已经理解了{ai_topic}。`

`只需要{time_promise}，我用{life_example}告诉你什么是{ai_topic}。`

Build this opening in five steps:

1. Extract the core role of every headline AI concept.
2. Choose an everyday system that an ordinary viewer already knows.
3. Map every concept one-to-one to a distinct element in that system.
4. Create the recognition contrast: the viewer discovers that a familiar behavior already contains the idea.
5. Add a short, credible time promise to lower the learning barrier.

Use three or four headline concepts by default. `{ai_topic}` may be their natural spoken list or a clear umbrella topic. When the user explicitly supplies different opening wording or a different concept count, preserve it and mark `opening.explicit_override: true` instead of forcing the default hook.

The first shot must:

- for a `suspense_question` about contrasting AI behavior, show the actual AI phenomenon or side-by-side contrast within the first second, then reveal the familiar analogy as the explanation bridge;
- for other hook types, show the familiar behavior, object, or situation within the first second;
- lead with a concrete scene or observable contrast rather than a professional definition or unexplained technical term;
- assume no technical background and make the one-to-one mapping visually understandable;
- deliver both the recognition contrast and the time promise, but keep the time promise in narration by default—do not add countdowns, clocks, progress rings, ticking timers, or equivalent decorative time graphics unless the user explicitly asks for them;
- reveal the three or four concept labels in spoken order and hold the final all-visible state long enough to read;
- keep exact editorial spelling on screen while allowing pronunciation-safe TTS forms in `spoken_text`;
- keep the physical top 10% of the frame blank.

Use `opening.concept_mappings` as the mapping source of truth. Every mapping records the concept, its core role, and its distinct life element. When the topic contains more than four candidates, group or select the three or four headline concepts during concept design; in Review as you go mode, include that choice and the mapping in concept approval.

Select `opening.hook_type` to vary the emotional lead while preserving the familiar-life mapping and time promise:

- `pain_point_reframe`: challenges the belief that the topic is too technical, then lowers the barrier with the familiar behavior.
- `suspense_question`: opens with a contrast question. When the question describes different AI outputs or behavior, visualize that real AI contrast first and introduce the familiar life example only as the answer bridge.
- `curiosity_reveal`: creates a surprising link between a frontier topic and an everyday behavior.
- `scenario_immersion`: starts with a concrete imagined scene; requires `life_example_scene_*`.

Legacy `life_mapping` remains supported for existing projects. For the four selectable hooks, the opening helper owns the approved wording; reserve custom templates for explicit user overrides.

## Short-form editorial intensity

When the user prefers a high-retention short-video style, allow memorable hyperbole, dramatic labels, conflict, and controversy in the hook and character arc. Phrases such as `一模一样` or a compressed transformation such as `从街头霸王蜕变为MVP` may be preserved when explicitly approved; do not automatically replace them with cautious academic qualifiers merely because the analogy is not documentary-complete.

Keep entertainment compression separate from the instructional core:

- It is acceptable to compress chronology, omit secondary context, or use a famous controversial moment as a symbol of a character conflict.
- Do not invent a direct quote, achievement, identity, or event. If an anecdote has disputed context, present the controversy or public impression rather than claiming one interpretation is proven fact.
- Let the opening and character framing be provocative; keep the AI mechanism, concept boundaries, causal sequence, and final takeaway technically correct.
- When virality and completeness conflict, shorten caveats and background before weakening the central AI explanation.

## Mandatory total–part–total structure

Every video's narration and storyboard must use a `总—分—总` structure unless the user explicitly requests another structure:

1. **总｜Opening overview:** use the life-mapping hook to introduce the familiar system and the same three or four headline concepts. Do not explain them in full yet.
2. **分｜Concept breakdown:** explain each introduced concept in a clear sequence. Give every concept at least one meaningful narration and visual beat, and show relationships between concepts when the explanation depends on them.
3. **总｜Concise close:** use one short synthesis sentence that resolves the video's main distinction or lesson, then immediately ask one easy, topic-specific question inviting viewers to reply in the comments. Do not add a second exhaustive recap or introduce a new headline concept.

Design the opening and closing as matching bookends. Their terminology, spoken/display spelling rules, and visual identity must agree. The concise summary should express the understanding earned in the middle rather than repeat every definition, and the final comment question should feel like the natural last beat.

Use this default ending cadence:

1. concise conclusion, usually one sentence beginning with `所以`;
2. comment hook, usually `评论区回复我，{topic-specific question}？`.

Avoid stacked endings such as a conclusion followed by `最后记住` and another full concept list before the hook.

## Default production profile

- Vertical 9:16, 1440×2560, 45fps.
- Reserve the top 10%, right 20%, and bottom 20% as blank platform-safe areas. Keep animation, labels, arrows, and cards inside the remaining center region; do not crop the scene.
- Use Xiaoxiao (`zh-CN-XiaoxiaoNeural`) as the default narration voice. If that backend is unavailable, use `Microsoft Huihui Desktop` only as a documented fallback.
- Use a consistent 1.2× narration tempo while preserving pitch.
- Keep `audio.narrator_voice` at `xiaoxiao` unless the user explicitly requests another supported voice.
- Keep about 1.0 second of silence between spoken shot segments.
- Increase narration consistently and limit peaks; do not normalize shots to visibly different loudness.
- Do not add subtitles unless requested. Concept labels and summary cards are screen graphics, not subtitles.
- Write every artifact under the current project directory. Use versioned folders and update `latest.mp4` only after QA passes.

Treat these as defaults. Follow explicit project-specific overrides.

## Narration voice parameter

- `audio.narrator_voice: "xiaoxiao"` (or an omitted field) selects the default Xiaoxiao neural voice configured by `audio.voice`, normally `zh-CN-XiaoxiaoNeural`.
- `audio.fallback_voice: "Microsoft Huihui Desktop"` is used only when Xiaoxiao cannot be reached and `audio.allow_voice_fallback` is true. Record both the requested and actual voice in QA.
- `audio.narrator_voice: "default"` explicitly selects the existing Windows TTS voice configured by `audio.voice` and `audio.base_rate`.
- `audio.narrator_voice: "mambo"` selects the optional local MamboTTS/GPT-SoVITS voice. Treat this value as explicit opt-in; never select it merely because the model is installed.
- Run `scripts/generate_narration.py project.json` for either backend. For Mambo, the script reuses a ready local API or starts the installed engine invisibly, generates and validates every WAV, then stops the engine it started unless `--keep-engine-running` is set.
- Locate MamboTTS through `audio.mambo.home`, `MAMBOTTS_HOME`, `--mambotts-home`, or the workspace convention `tools/mambotts/app`. Optional `audio.mambo.api_url` and `audio.mambo.speed` override the local endpoint and raw synthesis speed.
- The MamboTTS client code is MIT-licensed, but that does not grant rights to a third-party voice identity or voice model. Use Mambo only after the user explicitly requests it and accepts responsibility for the intended use; keep the default voice for unspecified requests.

## Non-negotiable invariants

- Preserve the latest user-approved concept definitions across narration, storyboard, and visuals. Do not reintroduce a rejected analogy or definition.
- Keep the two-sentence life-mapping hook, first-second concrete anchor, recognition contrast, time promise, three-or-four-concept order, and final all-visible state unless the user explicitly overrides the opening. For AI-behavior suspense questions, the concrete anchor is the real AI contrast and the familiar analogy follows as the bridge.
- Treat short time promises as spoken framing, not a reason to draw timers. Do not use countdowns, clocks, progress rings, ticking digits, or similar time visualizations unless explicitly requested.
- Keep the top, right, and bottom platform-safe zones blank. Use `Canvas` or equivalent centralized layout math so no animation, text, card, or arrow enters those zones.
- Preserve the `总—分—总` structure: opening concept overview, complete middle breakdown, and a closing synthesis grounded in the same approved concepts.
- End with one concise synthesis followed by one comment question; do not repeat the complete summary twice.
- Keep `spoken_text` separate from `display_text`. A screen may show `Multi-agent` while TTS receives `MultiAgent` to avoid an unnatural pause.
- Never trim narration tails to control shot spacing. Silence detection may measure leading and trailing silence, but must not modify the source waveform.
- Change pacing uniformly across all narration and animation. Never force-fit individual shots with different audio speed factors.
- Derive shot length from measured audio. If a shot is short, compress low-information lead-in time before compressing required actions, icon highlights, or final states.
- Treat a card, diagram, or split panel containing people or objects as a miniature scene: animate its entrance, the represented action, and the resulting state. A static pose inside an animated card is not sufficient when the narration describes movement, comparison, choice, or feedback.
- Preserve a clear visual hierarchy in dense shots. Separate definitions, quotations, diagrams, actions, and conclusions into distinct groups or sequential beats; do not stack unrelated elements or let labels, bubbles, arrows, and characters collide.
- Show quantitative labels only when a value is supported by the project or a cited source. When a metric is useful but no trustworthy value exists, use a scoped qualitative trend such as `战术执行失误率 ↓` rather than inventing percentages.
- Generate animation at the target frame rate. Do not claim duplicated frames are native high-frame-rate animation.
- Inspect dense or animated shots at entry, mid-action, and final-hold progress before full rendering; a single late preview cannot prove that motion is meaningful or collision-free. Validate the complete decode, resolution, frame rate, audio stream, subtitle policy, shot-boundary pauses, and full final syllables before delivery.

## Reusable scripts

- `scripts/init_project.py`: create a project config and artifact folders.
- `scripts/prepare_opening.py`: validate the life mapping and three or four opening concepts, then create or refresh shot 1 from the two-sentence hook.
- `scripts/validate_structure.py`: verify the opening, middle concept coverage, and closing summary before rendering or delivery.
- `scripts/generate_narration.py`: dispatch narration from `audio.narrator_voice`; use Xiaoxiao by default, document any Huihui fallback, or optionally run and validate local MamboTTS when explicitly requested.
- `scripts/generate_narration.ps1`: generate complete per-shot WAV files on Windows without tail trimming.
- `scripts/export_narration.py`: export the final `spoken_text` in shot order as plain paragraphs in `narration.md` beside the video project.
- `scripts/process_narration.py`: apply one tempo and gain profile to all WAV files.
- `scripts/compute_timing.py`: measure speech boundaries without editing audio and calculate shot frames.
- `scripts/validate_video.py`: verify the final MP4 and boundary pauses.
- `scripts/render_common.py`: scalable drawing helpers and platform-safe composition for topic-specific renderers.

Use scripts when their prerequisites are available. If a platform lacks Windows TTS or FFmpeg, preserve the same invariants with an available equivalent instead of weakening the workflow.

## Completion

Every generated video must include a `narration.md` beside the project artifacts. Preserve shot order and separate narration segments with blank lines, but include only the spoken words. Do not write a title, `镜头 X`, numbering, headings, storyboard content, actions, visual descriptions, cues, timing, or production notes.

Deliver the final MP4, `narration.md`, project config, and QA report. Report any requested default that could not be verified. Do not update `latest.mp4` when validation fails.
