# Narration and storyboard guidelines

## Approval gates

Confirm the execution mode before creating polished narration, a storyboard, pilot media, audio, frames, or video:

- In **One-click final video** mode, do not pause for intermediate approvals. Treat the user's supplied concept as authoritative, make minor production decisions consistently, and complete the internal pilot and QA checks before delivery.
- In **Review as you go** mode, the concept explanation is the first approval gate. Do not proceed to polished narration until the user confirms the definitions or analogy. Then pause again for narration and storyboard approval, and for pilot-shot approval before full media generation.

If the user changes a definition later, update every downstream shot that depends on it in either mode.

Use a pilot shot before full rendering when the visual density, character style, split-screen treatment, text animation, or action readability remains open. Request user approval only in Review as you go mode; inspect and refine the pilot internally in One-click final video mode.

## Domain-first analogy

Understand the comparison domain on its own terms before mapping AI concepts to it. A basketball video should describe basketball actions and decisions, not paste computer actions such as browsing or coding onto a player.

Distinguish these layers:

- atomic action or tool;
- one actor's learned compound technique or skill;
- one agent choosing and combining skills;
- multiple agents coordinating toward a shared outcome.

The exact definitions come from the approved project, not from this generic pattern.

## High-retention editorial framing

Decide the editorial intensity before polishing narration. When the user requests a short-video, traffic-oriented, or controversy-driven style:

- Preserve explicitly approved bold language and strong equivalence claims instead of automatically hedging every analogy.
- Use recognizable personas, dramatic before-and-after arcs, rivalry, conflict, and controversial moments to create curiosity and retention.
- Documentary completeness is not required: chronology may be compressed and secondary context omitted when that does not change the AI lesson.
- A controversial anecdote may represent public perception or conflict, but do not fabricate quotations or concrete achievements. Avoid presenting a disputed interpretation as settled proof when a short phrase such as `这句争议言论让很多人觉得` retains the same tension.
- Apply factual rigor most strongly to the AI concept chain. A provocative sports metaphor must not turn SFT into RL, RL into RLHF, or complete alignment into a guaranteed outcome.

In review materials, separate `editorial framing` from `technical mapping` so the user can deliberately approve a provocative hook while still correcting the instructional mechanism.

## Life-mapping opening shot

Every video begins with this two-sentence narration pattern unless the user explicitly overrides it:

`你每天{familiar_behavior}，其实已经理解了{ai_topic}。`

`只需要{time_promise}，我用{life_example}告诉你什么是{ai_topic}。`

Before writing those sentences, extract each concept's core role, choose one everyday system, and assign every concept a distinct life element. The mapping must be one-to-one, not a loose theme. If the user explicitly specifies different opening wording or a different number of concepts, record `opening.explicit_override: true` and preserve it.

Choose one `opening.hook_type` for the opening:

1. `pain_point_reframe`: challenge the belief that the topic needs an intimidating technical threshold, then turn to the familiar behavior.
2. `suspense_question`: ask why the same topic can appear brilliant or ineffective, then put the answer in the familiar behavior.
3. `curiosity_reveal`: connect a frontier topic to an everyday behavior with a surprising reveal.
4. `scenario_immersion`: place the viewer in a concrete life scene before naming the concept; fill `life_example_scene_*`.

Each option still includes a life mapping and time promise. Do not invent a fifth fixed hook; use a custom template only after an explicit user request.

Build the shot in this order:

1. For an AI-behavior `suspense_question`, use the first second to show the actual contrast being asked about—for example, one model answering coherently beside another fabricating an answer—then transition to the familiar analogy that explains it. For other hook types, show the familiar behavior, object, or situation first.
2. Complete the recognition contrast: the viewer realizes that the familiar behavior already contains the AI idea.
3. Speak the short time promise and show the life example that will carry the explanation. Do not turn the time promise into a timer, countdown, clock, progress ring, or equivalent graphic unless the user explicitly requests time visualization.
4. Reveal all three or four concept labels in narration order and hold the completed layout long enough to read.

Use a balanced three-card layout for three concepts or a compact 2×2 layout for four when appropriate. The concrete opening scene is the anchor; labels support it without covering the action. Required milestones are the first-second AI contrast or familiar scene, the analogy bridge, recognition contrast, spoken time commitment, each ordered concept reveal, and the final all-visible state.

The physical top 10% remains completely blank. “At the top of the screen” means the top of the safe content region below that blank area. If timing becomes tight, shorten empty setup and decorative motion first; never drop, overlap, or truncate a concept reveal.

Keep spoken and displayed forms independent. For example, narration may use `MultiAgent` for smooth TTS while the synchronized label displays `Multi-agent`.

## Mandatory total–part–total flow

Plan the whole video as three connected sections:

- **Opening overview (`总`):** use a familiar life system to introduce all three or four headline concepts and lower the learning barrier. This is an orientation shot, not the detailed lesson.
- **Concept breakdown (`分`):** explain every introduced concept. Allocate enough narration and visual action for the viewer to understand what it is, how it maps to the comparison domain, and how it differs from adjacent concepts.
- **Concise close (`总`):** state one short conclusion that resolves the main lesson, then ask one topic-specific question inviting a comment. The visual may briefly reunite the established concept cards, but the narration should not repeat every definition a second time.

The opening and closing must use the same concept names, count, order, color identity, and screen spelling. The close should synthesize what the middle taught; do not add a new headline concept or replace one of the introduced concepts. Transitions may connect sections, but cannot substitute for explaining a concept.

## Default ending cadence

End the narration with exactly two functional beats unless the user requests another ending:

1. one concise synthesis sentence, commonly beginning with `所以`;
2. one low-friction comment question, commonly `评论区回复我，{topic-specific question}？`.

Keep the question directly related to the lesson and easy to answer with a name, example, or opinion. Do not place `最后记住` plus another full recap between the synthesis and the comment question. The final visual can show the concise comparison during the synthesis, then switch emphasis to the comment prompt while retaining the established visual identity.

## Shot record

Each shot should specify:

- its section: `opening`, `explanation`, `transition`, or `summary`;
- which headline concepts it introduces, explains, or summarizes;
- `summary_text` and `comment_hook` for the final shot;
- narration and any TTS-only spelling;
- concept screen text and appearance cues;
- characters, props, and environment;
- action phases;
- required milestones;
- transition or final hold;
- accessibility or platform-safe constraints.

Screen text is a concise concept cue. Do not convert the full narration into captions unless subtitles are requested.

## Timing

Generate narration first. Measure actual audio and speech boundaries, then calculate video frames. Keep one tempo across all segments.

When shortening a shot:

1. reduce empty lead-in;
2. reduce decorative holds;
3. keep required action phases and their final readable state;
4. extend the shot if the narration still does not fit.

Do not remove the end of a waveform. Retain the complete narration file and add enough video duration to include its natural tail.

## Platform-safe composition

Reserve the configured safe areas before positioning text. By default, leave the top 10%, right 10%, and bottom 20% blank for the platform UI. Compose all animation, text, arrows, and cards inside those limits; do not let an arrowhead or card edge enter a forbidden side. Keep the principal layout centered on the physical centerline of the full frame instead of centering it in the leftover area created by the one-sided right inset. Create render canvases with `Canvas.from_video_config(video)` or use equivalent bounds-aware math, then inspect representative frames because metadata alone cannot prove the zones are empty.

Do not reserve a blank sports-footage region in opening shots unless the user explicitly asks for one. By default, use the full central composition for the stickman explanation: title, characters, action, and concept labels all align to the physical centerline of the complete frame. If the user does request external footage, treat its insertion box as an independent layer and keep it inside the configured safe areas.

## Animation, cards, and information hierarchy

When a card, comparison row, diagram, or split panel contains a character or object, treat that region as a miniature animated scene rather than a decorated static infographic:

1. bring the card or panel into the layout with a short, readable entrance;
2. animate the action named by the narration inside it, such as a ball traveling, a defender closing out, or a player changing direction;
3. reveal the consequence only after the action, such as a check mark, interference state, ranking badge, or concept label;
4. hold the completed state long enough to understand the relationship.

For several cards, stagger their entrances and action beats so the viewer knows where to look. Do not animate every element simultaneously, and do not count border pulses or card movement as a substitute for the actual narrated action.

In dense shots, group information by function and reading order. Definitions, quotations, diagrams, action scenes, metrics, and conclusions should occupy separate columns, rows, or timed phases. Avoid placing a speech bubble over a diagram, a label over a character, or a conclusion pill across another information group. If the layout feels crowded, remove decorative elements or sequence the information before reducing legibility.

Use metrics only when they clarify the mechanism. If a project or cited source supplies a trustworthy value, label the number and its scope. Otherwise use a scoped qualitative indicator such as `战术执行失误率 ↓`; do not invent a percentage merely to make a graphic look quantitative.

Preview motion-dependent shots at no fewer than three meaningful states: entry, mid-action, and final hold. Check visual focus, collisions, completed action, consequence order, and safe-area compliance at each state before rendering the full video.

## QA acceptance

- All approved concepts remain consistent.
- Spoken and displayed forms are correct.
- Required visual milestones appear in order.
- The first second shows either the real AI contrast for an AI-behavior suspense question or a familiar life element for other hooks; the analogy bridge, recognition contrast, time promise, and all three or four concept labels appear in spoken order unless explicitly overridden.
- Time promises are not visualized with timers, countdowns, clocks, or progress rings unless explicitly requested.
- Every introduced concept receives a middle explanation beat.
- The final screen preserves the established concepts and introduces no new headline concept.
- The narration ends with one concise synthesis and one topic-specific comment question, without a duplicate full recap.
- Every final syllable is complete.
- Cards and diagrams that describe actions show the actual action and its consequence, not only a static pose or decorative entrance.
- Dense layouts remain legible at entry, mid-action, and final hold, with no collisions between labels, bubbles, arrows, characters, or result badges.
- Any displayed numeric metric is supported; unsupported metrics use a clearly scoped qualitative trend without fabricated values.
- Shot-boundary pauses fall within tolerance.
- Resolution, frame rate, aspect ratio, audio, and subtitle policy match the config.
- The entire file decodes without errors.
- The top, right, and bottom platform-safe zones remain clear in representative frames.
