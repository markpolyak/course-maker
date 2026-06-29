# Command: `/course-maker lab init N [url] [slug]`

Scaffold lab N: create the directory, set up `starter/` per the course's LMS
adapter, copy CI templates, register the lab in `COURSE_STATE.md`.

`url` is the starter-repo URL. Required only for profiles that attach a remote
starter repo (e.g. `github-classroom`); profiles that distribute locally
(e.g. `local-zip`) do not use it.

`slug` is optional. If provided, the lab directory is `labs/<slug>/`.
If omitted, the directory is `labs/labN/` (e.g. `labs/lab1/`).

Example (github-classroom):
```
/course-maker lab init 1 https://github.com/org/lab1-backprop lab1-backprop
```
Example (local-zip):
```
/course-maker lab init 1 lab1-backprop
```

Let `LAB_DIR = labs/<slug>/` if slug given, else `labs/labN/`.

---

## Steps

1. **Create directory:**
   ```bash
   mkdir -p <LAB_DIR>
   ```

2. **Create `<LAB_DIR>history.md`:**
   ```markdown
   # Lab N — History

   (no entries yet)
   ```

3. **Create empty `<LAB_DIR>lab_spec.md` placeholder:**
   ```markdown
   # Lab N Spec — placeholder
   # Run /course-maker lab spec N to generate this file.
   ```

4. **Set up `<LAB_DIR>starter/` per the LMS adapter:**
   Read `<course-root>/lms_adapter.md` → "Lab init — starter setup" and follow
   it. This step is LMS-specific:
   - A remote-starter profile (e.g. `github-classroom`) attaches a public
     starter repo at `<LAB_DIR>starter` (via `git subtree add`) using `<url>`.
   - A local profile (e.g. `local-zip`) just creates an empty
     `<LAB_DIR>starter/` directory; `<url>` is unused.

   If `lms_adapter.md` has no such section, default to creating an empty
   `<LAB_DIR>starter/` directory.

5. **Copy CI workflow:**
   ```bash
   mkdir -p <LAB_DIR>starter/.github/workflows
   cp labs/shared/tests.yaml <LAB_DIR>starter/.github/workflows/tests.yaml
   ```

6. **Copy base conftest:**
   ```bash
   cp labs/shared/conftest_base.py <LAB_DIR>starter/conftest.py
   ```

6b. **Copy the grade reporter, if the course uses one:**
   ```bash
   [ -f labs/shared/grade_report.py ] && \
     cp labs/shared/grade_report.py <LAB_DIR>starter/grade_report.py
   ```
   Present only when `grade_reporter` is not `none` (installed by
   `/course-maker lab course-init` Phase 2a). If absent, labs run plain pytest.

7. **Add lab N row to `COURSE_STATE.md` Labs table.**
   Fill `Dir` = `<slug>` or `labN`, all status columns ❌.

8. **Commit:**
   ```bash
   git add -A && git commit -m "lab N: init starter"
   ```

---

## Notes

- If `labs/shared/conftest_base.py` or `labs/shared/tests.yaml` are placeholders,
  step 5 or 6 produces a placeholder in `<LAB_DIR>starter/`. The user must
  replace them with real content before `/course-maker lab tests N`.
- Any constraint on `<url>` (e.g. github-classroom requires the starter repo to
  already exist, or `git subtree add` fails) is documented in the profile's
  `lms_adapter.md` "Lab init — starter setup" section, not here — step 4 is
  LMS-agnostic.
