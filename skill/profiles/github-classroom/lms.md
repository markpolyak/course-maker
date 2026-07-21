# LMS Adapter: github-classroom (via `gh api`)

This file is copied verbatim to `<course-root>/lms_adapter.md` by
`/course-maker lab course-init` when the course profile is `github-classroom`.
The `/course-maker lab publish N` command reads it and executes the
steps below.

**Workflow summary:** push the `<LAB_DIR>starter/` git subtree to the
public starter repo, then sync individual files into the GitHub Classroom
template repo via `gh api`. GHC creates per-student forks with squashed
history, so a direct `git push` to the GHC repo would always conflict —
that's why we use the contents API instead.

Read `AGENTS.md` → `## Lab context` to get the GHC org and repo naming
pattern before starting.

---

## Lab init — starter setup

Used by `/course-maker lab init N <url> [slug]` (step 4) to attach the starter.
This profile keeps each lab's `starter/` as a git subtree of a public starter
repository.

```bash
git subtree add --prefix=<LAB_DIR>starter <url> main --squash
```

`<url>` must point to an existing GitHub repository — create it first, or the
subtree command fails.

---

## Step 1 — Push to starter repo (git subtree)

Get the URL from `AGENTS.md` Lab context → Starter repos table for lab N.

```bash
git subtree push --prefix=<LAB_DIR>starter <url> main
```

If the push fails because of diverged history, see "Recovery" below.

---

## Step 2 — Sync GHC repo via `gh api`

Resolve `$GHC_REPO` from `AGENTS.md` Lab context using the naming
pattern from `lms_defaults.yaml` (`ghc_repo_naming`, default `{N}-{student}`
for GHC fork mode). Substitute the variables (`{N}`, `{student}`, etc.)
from the per-lab context; check `AGENTS.md` Lab context for the resolved
value for this course.

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

**Note:** `lab_spec.md` and `history.md` are explicitly NOT in the sync
list. They are instructor-only.

---

## Step 3 — Update course repo

```bash
git add <LAB_DIR>
git commit -m "lab N: publish"
git push
```

---

## Step 4 — Update state

This step is performed by the skill, not this adapter:

- `COURSE_STATE.md`: set `published → ✅` for lab N.
- Append to `<LAB_DIR>history.md`:

  ```markdown
  ## [YYYY-MM-DD] Published

  **Starter repo:** <url>
  **GHC repo:** <ghc_repo>
  **Files synced:** exercises.ipynb, conftest.py, tests.py, requirements.txt, README.md, ...
  ```

---

## Recovery — `git subtree push` failure

If subtree push fails because of diverged history (common when GHC
squashed history collides with the local subtree):

```bash
# Inspect divergence
git fetch <starter-remote> main
git log <starter-remote>/main..HEAD -- <LAB_DIR>starter/
```

Two options:

1. **Force-replace starter repo content** (safe if starter repo has no
   external contributors):
   ```bash
   git subtree split --prefix=<LAB_DIR>starter -b lab-N-publish
   git push <starter-url> lab-N-publish:main --force-with-lease
   git branch -D lab-N-publish
   ```

2. **Manual sync via `gh api`** (skip Step 1 subtree push, do Step 2 only).
   Slower but avoids history conflicts. Acceptable if the starter repo
   and the GHC repo are the only consumers.

Ask the user before force-pushing.
