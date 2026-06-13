# Profile: local-zip

LMS-free publish workflow. Builds a self-contained zip of the student-facing
lab materials; you upload the zip wherever your course lives (an LMS course
page, share drive, email distribution list).

**Use this profile when:**

- You're evaluating the skill and don't want to commit to an LMS yet.
- Your LMS is not yet supported by any other profile.
- You publish materials by hand (institutional intranet, paper handouts,
  email).

**What this profile provides:**

- `lms.md` — the "build a zip" workflow copied to `<course-root>/lms_adapter.md`
  during `/course-maker lab course-init`.
- `lab_questions.yaml` — a single question (the delivery channel name) that
  the lab course-init wizard collects to make the lab publish summary
  meaningful.
- `lms_defaults.yaml` — empty; this profile has no LMS-specific defaults
  worth pre-filling.

**What this profile does NOT do:**

- Push to GitHub.
- Sync to any LMS via API.
- Embed any institution / instructor preferences. Those live in
  `~/.course-maker/defaults.yaml` (user_defaults) — see
  `skill/profiles/README.md`.
