# Profiles

A **profile** in this skill describes how labs get **published** — the LMS
adapter. It bundles:

- `lms.md` — the workflow the agent runs during `/course-maker lab publish`.
- `lab_questions.yaml` — the LMS-config questions asked during
  `/course-maker lab course-init`.
- `lms_defaults.yaml` — defaults for those questions (e.g. typical repo
  naming pattern).
- `README.md` — what the profile is for, when to use it.

A profile is **not** a personal preferences bundle. Instructor-specific
defaults (language, latex engine, audience, style, instructor name) live
in **user_defaults** — see below. Profile and user_defaults are orthogonal:
a `github-classroom` user and a `local-zip` user can both have the same
user_defaults (e.g. Russian + xelatex + a specific style).

A profile is also **not** a language. The course language and its
terminology dictionary live in
`skill/templates/course_conventions_{lang}.md` and
`skill/templates/lab_templates_{lang}.md`.

---

## Available profiles

- **`local-zip/`** — LMS-free. Bundles a zip of the student-facing
  materials; you upload the zip wherever your course lives. Use this when
  evaluating the skill or when no other profile matches your LMS.
- **`github-classroom/`** — GitHub Classroom via `gh api`. Pushes the
  starter subtree to a public repo and syncs files into the GHC-managed
  repository.

---

## How a profile is selected

The profile name is stored in `CLAUDE.md` → `## Course context` →
`Profile:`. Default: `local-zip`. The `course init` wizard asks for it on
first run and writes it into `CLAUDE.md`.

## How a profile is applied

- **`lab course-init`** reads `profiles/<name>/lab_questions.yaml` to know
  which LMS-config questions to ask, and copies `profiles/<name>/lms.md`
  to `<course-root>/lms_adapter.md`.
- **`lab publish`** reads `<course-root>/lms_adapter.md` and follows it.
  If the file is missing, the skill instructs the user to run
  `lab course-init`.

---

## user_defaults (instructor preferences across courses)

The skill supports a **user_defaults** file that holds preferences shared
across all courses an instructor teaches: language, LaTeX engine, default
audience description, default style, instructor name, and — if you use a grade
reporter — your autograder's grade labels. These pre-fill the
`/course-maker course init` dialog so you only answer them once for your
whole career.

### Location

`~/.course-maker/defaults.yaml`

Override with the environment variable `$COURSE_MAKER_HOME` if you want
to keep your config under XDG (`export COURSE_MAKER_HOME=$XDG_CONFIG_HOME/course-maker`)
or somewhere else. The skill uses `$COURSE_MAKER_HOME/defaults.yaml` if
the variable is set, otherwise `~/.course-maker/defaults.yaml`.

Works on Linux, macOS, and Windows (under Git Bash / PowerShell, where
`~` resolves to the user's home directory).

### Format

```yaml
# ~/.course-maker/defaults.yaml — instructor preferences across courses.
# All fields optional; empty string = ask the user fresh in course init.

default_language: ""           # e.g. "Russian"
default_slides_format: ""      # beamer / slidev  (empty = ask; course default beamer)
default_latex_engine: ""       # pdflatex / xelatex / lualatex  (beamer only)
default_audience: ""           # one paragraph; what students know coming in
default_style: ""              # one paragraph; rigor vs intuition, formula handling
default_instructor: ""         # name(s) for title slide / syllabus

# Grade-reporter labels — used only if you set grade_reporter (e.g. scoring_ci).
# Put your autograder's exact grade phrase here so it stays in your personal
# config, not in the shared course-language templates. Each overrides the
# course-language default from lab_templates.md when non-empty.
default_grade_output_label: "" # exact phrase your CI greps, e.g. a gradebook label
default_taskid_label: ""       # label before the variant number (default: "TASKID")
default_scoring_header: ""     # header printed atop the scoring block
```

### How it's created

The first time you run `/course-maker course init`, the wizard asks
content questions. At the end it offers:

> "Save these answers as your user_defaults? Next time, course init will
> pre-fill them. Press Enter to skip, or type a comma-separated list of
> fields to save (e.g. `language, latex_engine, instructor`)."

You can also create `~/.course-maker/defaults.yaml` by hand — copy the
format above.

### When user_defaults are read

At the start of `/course-maker course init`, before asking content
questions. Values are used as **suggested defaults** (press Enter to
accept, or type to override). The result is written into the course's
`CLAUDE.md` — the course no longer depends on user_defaults after init.

### What is NOT in user_defaults

- Institution name. This is per-course (you may teach at multiple
  institutions, or in joint programmes). Asked fresh every course.
- Profile (LMS). Profile is also per-course — same instructor may run
  one course on GHC and another with local-zip distribution.
- Anything course-specific (audience for THIS course, style for THIS
  course). The `default_*` values are suggestions, not enforcement.

---

## Writing your own profile

If you have an LMS not covered by existing profiles (Moodle, Canvas,
OpenEdX, internal portal with an API, etc.):

1. Copy `local-zip/` to `<your-lms-slug>/`.
2. Replace `lms.md` with your LMS-specific publish workflow.
3. Edit `lab_questions.yaml` to describe what your workflow needs
   (API endpoint URL, course ID, access token name from environment,
   etc.). Tokens themselves go in environment variables, never in
   files.
4. Set sensible `lms_defaults.yaml` (or leave it empty).
5. Update `README.md` to describe what your profile does.
6. Open a PR — your profile becomes available to others on next
   `git pull`.
