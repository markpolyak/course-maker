# /course-maker course update

Use when `course_plan.md` was edited manually (outside the skill).

1. Run `git diff course_plan.md` to detect changes.
2. For every lecture, seminar, or lab whose content changed in the diff:
   - Mark affected columns as ⚠️ in `COURSE_STATE.md`.
   - Append a note to the affected `history.md`.
3. Update `COURSE_STATE.md`.
4. Report: which sections changed, which materials are now ⚠️ and why.

For intentional structural edits (sessions added/removed, topics shifted), use
`/course-maker course plan update` instead — it applies the edit and then runs
this same cascade.
