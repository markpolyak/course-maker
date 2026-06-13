# Profile: github-classroom

LMS adapter for GitHub Classroom. Publishes lab materials by:

1. Pushing the `<LAB_DIR>starter/` git subtree to a per-lab public starter
   repository (the "template" of the GitHub Classroom assignment).
2. Synchronizing individual files into the GHC-managed repository (or per-
   student forks) via the GitHub REST API (`gh api`). This bypasses the
   squashed-history conflict caused by GHC repo creation.

**Use this profile when:**

- Your institution uses GitHub Classroom to distribute and autograde labs.
- You publish labs via per-lab starter repos and per-student forks.
- You have `gh` CLI installed and authenticated.

**What this profile provides:**

- `lms.md` — the GHC + `gh api` workflow copied to
  `<course-root>/lms_adapter.md` during `/course-maker lab course-init`.
- `lab_questions.yaml` — the LMS-config questions the wizard asks
  (GitHub org, GHC classroom org, repo naming pattern, per-lab starter
  URLs).
- `lms_defaults.yaml` — LMS-related defaults (default repo naming
  pattern `{N}-{student}`).

**What this profile does NOT do:**

- Embed instructor preferences (language, latex engine, style). Those
  belong in `~/.course-maker/defaults.yaml` (user_defaults) — see
  `skill/profiles/README.md`.
- Embed institution name or audience description. Those are course-level
  and live in `CLAUDE.md`.

If you're a `github-classroom` user with personal defaults (language,
latex engine, preferred style), `/course-maker course init` will offer to
save them as user_defaults the first time you run it.
