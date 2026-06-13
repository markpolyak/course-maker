# Command: `/course-maker lab publish N`

Publish lab N to wherever students will receive it. The concrete workflow
lives in `<course-root>/lms_adapter.md` (copied from the course profile
during `lab course-init`). This file is the dispatcher.

---

## Step 0 — Locate the LMS adapter

Read `<course-root>/lms_adapter.md`. This file was copied from
`skill/profiles/<name>/lms.md` when the user ran
`/course-maker lab course-init` (where `<name>` is the course profile,
default `generic`).

**If `lms_adapter.md` does not exist:**

Stop and show:
```
<course-root>/lms_adapter.md is missing.

This file defines how labs are published for your course. It is installed
by /course-maker lab course-init from the profile configured in CLAUDE.md
(Course context → Profile).

To install it:
  1. Check that CLAUDE.md → Course context → Profile is set
     (default: generic).
  2. Run /course-maker lab course-init.
  3. Re-run /course-maker lab publish N.

To choose a different LMS workflow, change the Profile field in CLAUDE.md
before re-running lab course-init. Available profiles are listed in
skill/profiles/.
```

Do not attempt to publish without `lms_adapter.md`. No fallback workflow.

---

## Step 1 — Read and execute the adapter

Read `<course-root>/lms_adapter.md` in full. It contains the
profile-specific publish steps (push to starter repo, sync GHC, upload zip,
etc.). Execute each step in order, asking the user for confirmation on
anything destructive (force-push, large file deletion).

The adapter is **the source of truth** for what gets published, in what
order, with what flags. The skill does not override or skip its steps.

---

## Step 2 — Update state (always performed by the skill)

After the adapter steps complete successfully:

- `COURSE_STATE.md`: set `published → ✅` for lab N.
- Append a publish entry to `<LAB_DIR>history.md`. The adapter's last
  step may have generated specific values to record (starter repo URL,
  GHC repo, files synced, bundle filename); include those.

If any adapter step fails, do not update state. Tell the user which step
failed and stop. State stays at `published → ❌` until the next successful
publish.
