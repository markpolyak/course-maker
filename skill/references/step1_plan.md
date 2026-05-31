# Step 1 — Lecture Plan

## Context to gather before writing

From `course_plan.md`:
- Section for lecture N: full content list, estimated time, prerequisites

From `CLAUDE.md` → `## Course context`:
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
| 1 | Course intro / motivation | ... | 3 min |
| 2 | ... | ... | ... |

---

## Detailed descriptions

### Slide 1 — [Title]
[2–4 sentences describing exactly what appears on the slide:
formulas, key points, diagram description, what the lecturer
should emphasize]

### Slide 2 — [Title]
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

- Maximum 20 slides total
- Each slide description must be concrete enough that a designer
  (or Claude in Step 4) could produce the slide without asking questions
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
