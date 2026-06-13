# Command: `/course-maker lab publish N`

Push the starter directory to the public starter repo, sync the GitHub
Classroom repo via the `gh` API, commit the publish in the course repo.

Read `CLAUDE.md` → `## Lab context` to get the GHC org and repo naming pattern
before starting.

---

## Step 1 — Push to starter repo (git subtree)

Get the URL from `CLAUDE.md` Lab context → Starter repos table for lab N.

```bash
git subtree push --prefix=<LAB_DIR>starter <url> main
```

If the push fails because of diverged history, see "Recovery" below.

---

## Step 2 — Sync GHC repo via `gh` API

GitHub Classroom creates its own copy of the starter repo (the GHC repo) with
squashed history — direct `git push` does not work. Sync individual files via
the GitHub REST API instead.

Read `CLAUDE.md` to find the GHC repo name for lab N.

For each student-facing file in `<LAB_DIR>starter/`:
- `exercises.ipynb`
- `conftest.py`
- `tests.py`
- `requirements.txt`
- `README.md`
- `datasets_info.md` (if it exists)
- `.github/workflows/tests.yaml`

Run:

```bash
SHA=$(gh api repos/$GHC_REPO/contents/$FILE --jq '.sha // empty' 2>/dev/null)
CONTENT=$(base64 < <LAB_DIR>starter/$FILE)
if [ -n "$SHA" ]; then
  gh api repos/$GHC_REPO/contents/$FILE --method PUT \
    --field message="sync: lab N update" \
    --field content="$CONTENT" \
    --field sha="$SHA"
else
  gh api repos/$GHC_REPO/contents/$FILE --method PUT \
    --field message="sync: lab N initial publish" \
    --field content="$CONTENT"
fi
```

**Note:** `lab_spec.md` and `history.md` are explicitly NOT in the sync list.
They are instructor-only.

---

## Step 3 — Update course repo

```bash
git add <LAB_DIR>
git commit -m "lab N: publish"
git push
```

---

## Step 4 — Update state

- `COURSE_STATE.md`: published → ✅.
- Append to `<LAB_DIR>history.md`:
  ```markdown
  ## [YYYY-MM-DD] Published

  **Starter repo:** <url>
  **GHC repo:** <ghc_repo>
  **Files synced:** exercises.ipynb, conftest.py, tests.py, requirements.txt, README.md, ...
  ```

---

## Recovery — `git subtree push` failure

If subtree push fails because of diverged history (common when GHC squashed
history collides with the local subtree):

```bash
# Inspect divergence
git fetch <starter-remote> main
git log <starter-remote>/main..HEAD -- <LAB_DIR>starter/
```

Two options:

1. **Force-replace starter repo content** (safe if starter repo has no external
   contributors):
   ```bash
   git subtree split --prefix=<LAB_DIR>starter -b lab-N-publish
   git push <starter-url> lab-N-publish:main --force-with-lease
   git branch -D lab-N-publish
   ```

2. **Manual sync via gh API** (skip Step 1 subtree push, do Step 2 only).
   Slower but avoids history conflicts. Acceptable if the starter repo and the
   GHC repo are the only consumers.

Ask the user before force-pushing.
