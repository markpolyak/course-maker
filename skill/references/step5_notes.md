# Step 5 — Speaker Notes

## Context to gather before writing

1. `lectures/NN/plan.md` — content and timing per slide
2. `lectures/NN/slides.tex` — exact slide order and titles
   (if it exists; if not, use plan.md order)
3. `CLAUDE.md` → `## Course context` — audience, tone, language
4. `lectures/NN/history.md` — any tone or pacing feedback from previous rounds
5. `course_conventions.md` (course root) — terminology dictionary and language rules

## What speaker notes are (and are not)

**Are:** Live text the lecturer reads, adapts, and delivers aloud.
Natural spoken language, first person or direct address. Includes cues
for pacing, emphasis, and interaction with the audience.

**Are not:** A bullet-point summary of the slide. Not a formal transcript.
Not a repetition of slide content.

## Output format: `lectures/NN/speaker_notes.md`

**Generate all text in the course language** (from CLAUDE.md → Course context).
The examples below show format and tone — produce the actual notes in the course language.

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
