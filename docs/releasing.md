# Releasing

A release ships one artifact: `course-maker-<version>.zip`, the archive you
upload into Claude Cowork. Its single top-level folder is `course-maker/`,
containing the contents of `skill/` (`SKILL.md`, `references/`, ...). The same
zip also installs into Claude Code / Codex / Cursor by unzipping it into their
skills directory — see the README **Installation** section (Option A).

**The version is the git tag — nothing else to bump.** The tag you choose when
drafting the release (e.g. `v1.3.0`) becomes the version: the zip is named from
it, and `scripts/package.sh` stamps it into the packaged `SKILL.md` frontmatter:

- `metadata.version` — the semver form, with the leading `v` stripped (`1.3.0`).
- `description` — a ` · v1.3.0` suffix is appended so the version shows in the
  Cowork skill card (the card renders the description text). Note: Cowork does
  not display `metadata.version` itself, which is why the suffix exists.

The committed `skill/SKILL.md` keeps a `0.0.0-dev` placeholder and no suffix, so
symlink installs (Claude Code / Codex / Cursor) are unaffected — stamping happens
only in the build, never in the repo. Use `vMAJOR.MINOR.PATCH` for the tag.

## Publish a release (GitHub UI — recommended)

1. Make sure everything you want shipped is committed and pushed to `main`.
   The archive is built from the tagged commit, not your local working tree.
2. On GitHub: **Releases → Draft a new release**.
3. **Choose a tag → Create new tag**, type the version (e.g. `v1.3.0`), target
   `main`.
4. Click **Generate release notes** (fills the changelog from merged commits/PRs).
   Edit the text if you like.
5. Click **Publish release**.

The `release` workflow then builds `course-maker-v1.3.0.zip` and attaches it to
the release. Watch it under the **Actions** tab; when it finishes the zip appears
under the release's **Assets**. Download it and upload it into Cowork.

## Publish a release (CLI alternative)

Same result from the terminal, if you prefer:

```bash
gh release create v1.3.0 --generate-notes
```

This creates the tag and the release; the workflow attaches the zip as above.

## Build the zip locally (no release)

To produce the archive without cutting a release — e.g. to test the Cowork
upload — run:

```bash
make package          # dist/course-maker-<git-describe>.zip
./scripts/package.sh v1.3.0   # or force a specific version string
```

Local builds package **committed** files only (`git archive` from `HEAD`), so
commit first. A build from a dirty tree gets a `-dirty` suffix in its name as a
reminder that it is not a clean release artifact.
