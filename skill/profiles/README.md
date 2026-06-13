# Profiles

A **profile** is a bundle of an instructor's personal conventions:
default values for the `course init` dialog, and the LMS-specific workflow
for publishing labs. Profiles let the universal skill stay LMS- and
instructor-neutral while supporting concrete real-world setups.

A profile is **not** a language (course conventions and lab templates live
in `skill/templates/course_conventions_{lang}.md` and
`skill/templates/lab_templates_{lang}.md`). A profile and a language are
orthogonal: an instructor with `profile: polyak` can teach a course in
English, Russian, or any other language.

---

## How a profile is selected

The profile name is stored in `CLAUDE.md` → `## Course context` →
`Profile:`. Default: `generic`. The `course init` wizard asks for it on
first run and writes it into `CLAUDE.md`.

## How a profile is applied

- **`course init`** reads `profiles/<name>/course_defaults.yaml` and uses
  its values as **suggested defaults** in the dialog. The user can press
  Enter to accept, or type a different value to override.
- **`lab course-init`** copies `profiles/<name>/lms.md` to
  `<course-root>/lms_adapter.md`. This file becomes the LMS workflow for
  the course.
- **`lab publish`** reads `<course-root>/lms_adapter.md` and follows it.
  If the file is missing, the skill instructs the user to run
  `lab course-init` to install the profile's adapter.

After `course init` finishes, the profile is "baked in" — the course no
longer depends on the profile directory existing. You can change
`Profile:` in CLAUDE.md and re-run `course init`, but only newly-asked
defaults will use the new profile; existing values stay.

---

## Profile contents

Every profile directory contains:

- **`README.md`** — describes the profile (audience, typical institution,
  LMS choice).
- **`course_defaults.yaml`** — defaults for the `course init` dialog.
  Keys: `institution`, `default_audience`, `default_style`,
  `default_language`, `default_latex_engine`, `ghc_org`, `ghc_repo_naming`,
  and others as needed. Values may be empty strings — they become "no
  default, ask the user fresh".
- **`lms.md`** — the LMS publish workflow. Copied verbatim to the course
  root as `lms_adapter.md`. Should contain step-by-step instructions for
  pushing student materials to wherever they need to go.

---

## Available profiles

- **`generic/`** — no LMS, local-zip publish. Use this if you don't have
  a specific LMS yet, want to keep the workflow minimal, or are evaluating
  the skill.
- **`polyak/`** — Master's-level CS courses at ITMO University.
  GitHub Classroom via `gh api`. Russian course materials by default.
  This is also the worked example for "how to write your own profile".

---

## Writing your own profile

1. Copy `generic/` to `<your-slug>/`.
2. Edit `course_defaults.yaml` with your defaults.
3. Replace `lms.md` with the workflow for your LMS (Moodle, Canvas,
   OpenEdX, internal system, etc.).
4. Update `README.md` to describe what your profile is for.
5. Open a PR if your profile would be useful as an example for others —
   it should not contain secrets (tokens go in environment variables,
   not files).
