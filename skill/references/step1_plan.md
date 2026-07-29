# Step 1 — Lecture Plan

> **Session directory.** Paths below use `lectures/NN/`. For the seminar mirror
> `/course-maker seminar plan N`, substitute `seminars/NN/` for `lectures/NN/`
> throughout — the structure is identical.

## Context to gather before writing

From `course_plan.md`:
- `## Sessions` table — find the row for lecture N to get its week and position
- `## Lectures` → `### Lecture N` — topics, estimated time, prerequisites within course,
  announce-only sections

From `AGENTS.md` → `## Course context`:
- Audience background
- Rigor vs intuition preference
- Which sections to cover fully vs announce-only

From `course_conventions.md` (course root):
- Terminology dictionary and language rules

From `history.md` (if exists):
- Previously rejected slide structures
- Approved decisions to preserve
- Any sections the user asked to expand or compress

## Output format: `lectures/NN/plan.md`

```markdown
# Lecture N — [Title]

**Total time:** [planned duration from course_plan.md]  
**Slides:** NN   ← content slides; both fields are read back to calibrate pace

---

## Slide plan

| # | Title | Content summary | Time |
|---|-------|----------------|------|
| 1 | Title slide | — | 1 min |
| 2 | Outline | — | 1 min |
| 3 | Course intro / motivation | ... | 3 min |
| 4 | ... | ... | ... |

---

## Detailed descriptions

### Slide 3 — [Title]
[2–4 sentences describing exactly what appears on the slide:
formulas, key points, diagram description, what the lecturer
should emphasize]

### Slide 4 — [Title]
...

---

## Timing table

| Block | Slides | Time |
|-------|--------|------|
| Block 1: ... | 1–5 | 20 min |
| Block 2: ... | 6–12 | 35 min |
| Buffer / questions | — | 10 min |
| **Total** | | **must equal the planned duration** |

## Cut candidates
[If lecture runs long, these slides can be compressed or skipped
without breaking the logical flow:]
- Slide N: ...
```

## Constraints

- Slide numbering is absolute: slide 1 = title slide, slide 2 = outline, content starts at slide 3.
  Never start content slides at 1. Slides 1 and 2 need no detailed description — they are fixed.
- Slide count follows the planned duration, not a fixed cap. Take the duration
  from `course_plan.md` (`### Lecture N` → `**Estimated time:**`, else
  `## Overview` → `**Standard duration:**`) and aim for **3–6 minutes per
  content slide** — about 4.5 by default, which lands near 20 content slides
  for 90 minutes and near 30 for 135. Content slides exclude title, outline,
  and closing. Leaving the band is fine when the material demands it; say why
  in the plan.
- Calibrate to the instructor's real pace instead of the 4.5 default: if
  earlier `lectures/*/plan.md` exist, read their `**Total time:**` and
  `**Slides:**` and use their median minutes per content slide. A lecturer who
  moves fast has already produced denser plans — follow the course's own
  history rather than the default.
- Each slide description must be concrete enough that a designer
  (or the agent in Step 4) could produce the slide without asking questions
- For "announce-only" sections: 1–2 slides max, no derivations,
  just motivation + pointer to where it's covered fully
- Mark slides that contain a formula with `[formula]` tag in the summary
- Mark slides that need a figure with `[figure]` tag in the summary —
  these will drive Step 2

## Common mistakes to avoid

- Overloading slides 1–3 with definitions (students tune out)
- Putting too many formulas on one slide
- Forgetting a "what we learned" closing slide
- Not specifying which slides are "announce-only" when the plan says so
- Forward references to later slides ("we will cover this on slide X", "more detail in the next section") — forbidden on any slide except the closing one
- References to the next lecture: **maximum 1 per entire lecture**, only on the closing slide, and only if genuinely useful; omitting them entirely is preferred
