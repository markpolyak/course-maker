# Step 5 — Speaker Notes

> **Session directory.** Paths below use `lectures/NN/`. For the seminar mirror
> `/course-maker seminar notes N`, substitute `seminars/NN/` for `lectures/NN/`
> throughout — the structure is identical.

## Context to gather before writing

1. `lectures/NN/plan.md` — content and timing per slide
2. `lectures/NN/slides.tex` — exact slide order and titles
   (if it exists; if not, use plan.md order)
3. `AGENTS.md` → `## Course context` — audience, tone, language
4. `lectures/NN/history.md` — any tone or pacing feedback from previous rounds
5. `course_conventions.md` (course root) — terminology dictionary and language rules

## What speaker notes are (and are not)

**Are:** Live text the lecturer reads, adapts, and delivers aloud.
Natural spoken language, first person or direct address. Includes cues
for pacing, emphasis, and interaction with the audience.

**Are not:** A bullet-point summary of the slide. Not a formal transcript.
Not a repetition of slide content.

## Modes

`/course-maker notes N [minimal|medium|detailed]`. Resolve in this order: the
command argument, else `Notes mode:` in `AGENTS.md` → `## Course context`, else
`medium`. The mode sets how much of the delivery is written out — it changes
nothing about the format, the section structure, or the tone rules below.

| Mode | Written out | Use when |
|------|-------------|----------|
| `minimal` | Opening and closing lines, definitions and statements; the rest as cues and stage directions | You know the material cold and need prompts, not a script |
| `medium` (default) | Full text for motivation, definitions, and derivations; cues for routine passages | Normal preparation |
| `detailed` | Near-verbatim script throughout | First delivery, a substitute lecturer, or turning the lecture into text |

**Verbatim is reserved for wording that matters** — opening and closing lines,
definitions and theorem statements, transitions between blocks, and the framing
sentence of a hard derivation. Those stay written out in every mode, `minimal`
included; everything else scales with the mode. So a greeting is a deliberate
opening line, not a leftover — but never pair a written-out greeting with a
slide body reduced to bullet points. That hybrid is the defect this section
exists to prevent.

## Volume must match the planned timing

Notes that read as a summary while `plan.md` allots the slide 4 minutes are the
most common defect in this step. Anchor volume to time:

    target words for a slide ≈ factor × speech rate × planned minutes

Speech rate comes from `AGENTS.md` → `## Course context` → `Speech rate:`.
If the field is absent, assume 110 wpm and say so in the final report.

| Mode | factor | 4-min slide at 110 wpm |
|------|--------|------------------------|
| `minimal` | 0.15–0.25 | 65–110 words |
| `medium` | 0.35–0.55 | 155–240 words |
| `detailed` | 0.85–1.10 | 375–485 words |

Bands are **per slide, not a global total** — a total that balances out still
hides one slide of three sentences sitting next to one of three paragraphs.

Two limits of this estimate. Do not silently compensate for them; mention them
when they apply:
- A derivation slide spends time at the board in silence, so it needs fewer
  words per minute than a narrative slide.
- Per-slide timing comes from `plan.md`. If a slide has no timing there, split
  its block's time evenly across the block's slides and say that you did.

## Output format: `lectures/NN/speaker_notes.md`

**Generate all text in the course language** (from AGENTS.md → Course context).
The examples below show format and tone at `medium` density — produce the
actual notes in the course language, at the resolved mode's density.

````markdown
# Lecture N — Speaker notes   ← translate heading to course language

**Total time:** 85–90 min   ← translate label to course language

---

## Slide 1 — [Title]   ← translate "Slide" to course language

Good morning. Today we are working out why...

[*Point to the slide title. Pause 3–5 seconds.*]

Before we get to the formulas, let's agree on what...

**Key term** — this is not just a mathematical definition, it's...

---

## Slide 2 — [Title]

⏱ *Checkpoint: ~8 min from the start*   ← translate label to course language

...

---

## Slide N — Summary   ← translate "Slide" and "Summary" to course language

So today we covered three things...

[*Don't rush. Give students time to write.*]

<!-- A reference to the next lecture is allowed only here, on the closing slide,
     and at most once per presentation. Omit if there is no compelling reason. -->

---

## Timing table   ← translate heading to course language

| Block | Slides | Time |   ← translate column headers to course language
|-------|--------|------|
| Introduction | 1–3 | 10 min |
| ... | ... | ... |
| **Total** | | **87 min** |

## What can be cut   ← translate heading to course language

If time is short, slide X can be skipped without breaking the logical flow:
announce that the topic is out of scope and give a reference.
````

## Chunking protocol (identical to the slides path)

Output is ALWAYS chunked — do not generate the whole file in one shot.

- **Chunk 0** = header + slides 1–5.
- **Chunk K (K≥1)** = slides `[5K-4 … min(5K, total)]`.
- **Chunk last** = timing table + what-can-be-cut section.

Append each chunk to `speaker_notes.md` immediately; do not pause between
chunks (auto-chain to the end). **Chunking is not a review cycle:** the user
approves the finished notes, not each chunk. Do not ask for approval between
chunks.

**Resuming:** `/course-maker notes N next` reads `speaker_notes.md`, finds the
last completed slide, and continues from there.

## Final self-check (after the last chunk)

Count the words actually written per slide and report **in chat**, not in
`speaker_notes.md` — that file is the lecturer's, keep the arithmetic out of it:

```
Mode: medium · speech rate: 110 wpm (from AGENTS.md)

| Slide | Words | Planned | Target band |   |
|-------|-------|---------|-------------|---|
| 7     | 40    | 4 min   | 155–240     | ⚠ |
| 8     | 210   | 2 min   | 75–120      | ⚠ |
```

Name the mode and the speech rate used, so the numbers can be judged. Flag
every slide outside its band and offer to expand or trim those — do not rewrite
them unasked. If most slides land short, say so plainly: that is the summary
drift this step is prone to, and the fix is regeneration, not patching.

## Formatting conventions

- `[*Stage direction in italic brackets*]` — director's note: where to point,
  pacing, pause, audience question. Write stage directions in course language.
- `**Bold**` — term to emphasize verbally
- `⏱ Checkpoint` — after each content block, with cumulative time from the start.
  Write the label in course language.
- Plain text — what to say

## Tone rules (read Course context first)

- Intuition before formula: explain the meaning before showing the equation.
  "What does λ₂ tell us physically? It's the mean-square bandwidth of the
  spectrum — essentially, how spread out the signal's energy is. Now the formula:"
- Ask questions where natural: "What do you think will happen if...?"
  but don't over-do it — max 1–2 per block.
- No forward references to later slides ("we will return to this", "see slide X") — forbidden except on the closing slide.
- Next-lecture mentions: **maximum 1 per entire set of notes**, only on the closing slide, omit if not necessary.
- Pacing cues are not optional: at least one `[*Pause*]` or
  `[*Let them write*]` per complex derivation. Write cues in course language.
- Academic but alive: no "thus it can be concluded that" stiffness.

## Iteration handling

If the user says "too formal", "too casual", "too long for this slide":
- Fix only the affected slides
- Append to history.md what the issue was and what register was adjusted
