# Profile: polyak

Personal profile for Mark Polyak's courses.

**Defaults:**
- Language: Russian (slides, speaker notes, lab materials)
- LaTeX engine: xelatex (Unicode + Cyrillic support without inputenc)
- LMS: GitHub Classroom synchronized via `gh api`
- Repo naming: `{N}-{student}` (GitHub Classroom fork mode — each student's
  fork lives at a per-student repo)

**Audience and institution defaults are intentionally left empty** —
they vary across courses (Bachelor's CS, Master's AI, postgraduate
research), so it's faster to answer them per-course than to maintain a
single default.

**To use this profile:**

1. In your course `CLAUDE.md` → `## Course context`, set `Profile: polyak`.
2. Run `/course-maker course init` — Russian / xelatex are pre-filled.
3. Run `/course-maker lab course-init` — copies `lms.md` to
   `<course-root>/lms_adapter.md` for the lab pipeline to use.

This profile also serves as a worked example for writing your own
profile — see `skill/profiles/README.md`.
