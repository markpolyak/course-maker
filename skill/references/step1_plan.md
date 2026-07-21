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

**Total time:** 85–90 min  
**Slides:** NN

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
| **Total** | | **85–90 min** |

## Cut candidates
[If lecture runs long, these slides can be compressed or skipped
without breaking the logical flow:]
- Slide N: ...
```

## Constraints

- Slide numbering is absolute: slide 1 = title slide, slide 2 = outline, content starts at slide 3.
  Never start content slides at 1. Slides 1 and 2 need no detailed description — they are fixed.
- Maximum 20 content slides (not counting title, outline, and closing/summary slides)
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
