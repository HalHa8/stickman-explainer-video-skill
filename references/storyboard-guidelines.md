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

## Mandatory opening shot

Every video begins with this narration pattern unless the user explicitly overrides it:

`如果把AI放到{domain}，{concept_list}，其实一下就能听懂。`

Use three or four headline concepts. Format them as `A、B和C` or `A、B、C和D`. The wording `放到` and `其实一下就能听懂` is part of the standard opening. Adapt only the domain and concept names.

If the user explicitly specifies different opening wording or a different number of concepts, use it as an approved override and record `opening.explicit_override: true`. Do not silently rewrite the user's opening to match the default count.

Build the shot in this order:

1. Show `如果把AI放到{domain}？` at the top of the safe content area, below the blank platform reserve.
2. Reveal concept 1 when its name is spoken.
3. Reveal every remaining concept in the same way and in narration order.
4. Hold the completed layout with all three or four labels readable before the shot ends.

Use a balanced three-card layout for three concepts or a compact 2×2 layout for four when appropriate. A domain-specific character, prop, or background may enter during the opening, but it must not compete with the question or delay the concept reveals. The required milestones are the question being readable, each ordered concept reveal, and the final all-visible state.

The physical top 10% remains completely blank. “At the top of the screen” means the top of the safe content region below that blank area. If timing becomes tight, shorten empty setup and decorative motion first; never drop, overlap, or truncate a concept reveal.

Keep spoken and displayed forms independent. For example, narration may use `MultiAgent` for smooth TTS while the synchronized label displays `Multi-agent`.

## Mandatory total–part–total flow

Plan the whole video as three connected sections:

- **Opening overview (`总`):** introduce the domain and all three or four headline concepts. This is an orientation shot, not the detailed lesson.
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

Reserve the configured safe area before positioning text. Compose in a logical design space, scale the complete scene uniformly, and place it below the top safe region. Inspect representative frames; metadata alone cannot prove the safe area is empty.

## QA acceptance

- All approved concepts remain consistent.
- Spoken and displayed forms are correct.
- Required visual milestones appear in order.
- The standard opening question and all three or four concept labels appear in spoken order, unless explicitly overridden.
- Every introduced concept receives a middle explanation beat.
- The final screen preserves the established concepts and introduces no new headline concept.
- The narration ends with one concise synthesis and one topic-specific comment question, without a duplicate full recap.
- Every final syllable is complete.
- Shot-boundary pauses fall within tolerance.
- Resolution, frame rate, aspect ratio, audio, and subtitle policy match the config.
- The entire file decodes without errors.
