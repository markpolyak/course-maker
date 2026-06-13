# LMS Adapter: generic (local zip)

This file is copied verbatim to `<course-root>/lms_adapter.md` by
`/course-maker lab course-init` when the course profile is `generic`.
The `/course-maker lab publish N` command reads it and executes the
steps below.

This adapter does not assume any LMS. It produces a self-contained zip
of the student-facing lab materials; you upload the zip to wherever
your course lives (Moodle, Canvas, email, internal portal).

If you have a real LMS, copy `profiles/generic/` to
`profiles/<your-lms>/`, replace this file with the LMS-specific workflow,
and switch your course profile.

---

## Step 1 — Build the student bundle

From the course root:

```bash
LAB_DIR="labs/<resolved-from-state>"
cd "${LAB_DIR}/starter"
zip -r "../../student-bundle-lab${N}.zip" . \
  --exclude '.git/*' --exclude '__pycache__/*' --exclude '.pytest_cache/*'
cd -
```

The zip contains: `exercises.ipynb`, `conftest.py`, `tests.py`,
`requirements.txt`, `README.md`, `datasets_info.md` (if present),
`.github/workflows/tests.yaml`.

**Excluded from the zip:** `.git/`, `__pycache__/`, `.pytest_cache/`.

**Never in the zip:** `lab_spec.md`, `history.md` — these live in
`labs/labN/` (one level up from `starter/`) and are instructor-only.

---

## Step 2 — Upload the bundle

This step is manual. Take `student-bundle-labN.zip` from the course root
and upload it to your students' delivery channel:

- LMS course page (Moodle, Canvas, OpenEdX, etc.) — "add resource" → zip
- Internal share drive / cloud folder
- Email distribution
- Anything else

The skill does not automate this step in the generic profile. If you find
yourself uploading the same way every course, that's a sign you should
write a custom profile with an automated `lms.md`.

---

## Step 3 — Commit the course repo

```bash
git add "${LAB_DIR}"
git commit -m "lab ${N}: publish (bundle: student-bundle-lab${N}.zip)"
git push
```

The zip itself does not need to be committed unless you want a versioned
record of every published bundle.

---

## Step 4 — Update state

This step is performed by the skill, not this adapter:

- `COURSE_STATE.md`: set `published → ✅` for lab N.
- Append publish entry to `<LAB_DIR>history.md`:

  ```markdown
  ## [YYYY-MM-DD] Published (generic profile)

  **Bundle:** student-bundle-lab${N}.zip
  **Delivered via:** <fill in: LMS / email / share drive>
  ```
