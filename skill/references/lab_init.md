# Command: `/course-maker lab init N <url> [slug]`

Scaffold lab N: create the directory, attach the starter repo as a git subtree,
copy CI templates, register the lab in `COURSE_STATE.md`.

`slug` is optional. If provided, the lab directory is `labs/<slug>/`.
If omitted, the directory is `labs/labN/` (e.g. `labs/lab1/`).

Example:
```
/course-maker lab init 1 https://github.com/org/lab1-backprop lab1-backprop
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

4. **Add starter repo as git subtree:**
   ```bash
   git subtree add --prefix=<LAB_DIR>starter <url> main --squash
   ```

5. **Copy CI workflow:**
   ```bash
   mkdir -p <LAB_DIR>starter/.github/workflows
   cp labs/shared/tests.yaml <LAB_DIR>starter/.github/workflows/tests.yaml
   ```

6. **Copy base conftest:**
   ```bash
   cp labs/shared/conftest_base.py <LAB_DIR>starter/conftest.py
   ```

7. **Add lab N row to `COURSE_STATE.md` Labs table.**
   Fill `Dir` = `<slug>` or `labN`, all status columns ❌.

8. **Commit:**
   ```bash
   git add -A && git commit -m "lab N: init starter subtree"
   ```

---

## Notes

- If `labs/shared/conftest_base.py` or `labs/shared/tests.yaml` are placeholders,
  step 5 or 6 produces a placeholder in `<LAB_DIR>starter/`. The user must
  replace them with real content before `/course-maker lab tests N`.
- The starter repo URL must point to an existing GitHub repository — create it
  first. The subtree command will fail otherwise.
