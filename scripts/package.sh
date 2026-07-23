#!/usr/bin/env bash
# Build the Cowork / Agent-Skills install archive from the committed skill/ tree.
#
#   ./scripts/package.sh            # version from `git describe --tags`
#   ./scripts/package.sh v1.3.0     # explicit version (used by CI on tag push)
#
# Produces dist/course-maker-<version>.zip whose single top-level folder is
# course-maker/ (the skill name Agent-Skills loaders expect), containing the
# contents of skill/ (SKILL.md, references/, profiles/, templates/, ...).
#
# The tree is taken from HEAD via `git archive`, so:
#   - only committed files are included (commit before packaging),
#   - ignored cruft (.DS_Store, __pycache__, *.pyc) is excluded automatically.
#
# The version (from the git tag) is stamped into the packaged SKILL.md:
#   - metadata.version   <- semver form (leading "v" stripped)
#   - description         <- gets a " · v<version>" suffix so it shows in the
#                            Cowork card, which renders the description text
# The committed skill/SKILL.md keeps a 0.0.0-dev placeholder and no suffix, so
# symlink installs (Claude Code / Codex / Cursor) are untouched.
set -euo pipefail

cd "$(dirname "$0")/.."

VERSION="${1:-$(git describe --tags --always --dirty 2>/dev/null || echo dev)}"
VERSION_NO_V="${VERSION#v}"   # metadata.version is conventionally semver, no "v"
OUT="dist/course-maker-${VERSION}.zip"

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

# Extract the committed skill/ tree into STAGE/course-maker/.
mkdir -p "$STAGE/course-maker"
git archive HEAD:skill | tar -x -C "$STAGE/course-maker"

SKILL="$STAGE/course-maker/SKILL.md"

# Stamp the version into the frontmatter. fm counts the --- fences: fm==1 is
# inside the frontmatter; the second --- closes it, and just before it we append
# a folded continuation line to the (last) description key.
awk -v ver="$VERSION" -v ver_no_v="$VERSION_NO_V" '
  /^---[ \t]*$/ {
    fm++
    if (fm == 2) { print "  \xc2\xb7 " ver; print; next }
    print; next
  }
  fm == 1 && $0 == "  version: \"0.0.0-dev\"" {
    print "  version: \"" ver_no_v "\""; next
  }
  { print }
' "$SKILL" > "$SKILL.tmp" && mv "$SKILL.tmp" "$SKILL"

# Fail loudly if the placeholder line was not replaced (e.g. frontmatter drifted).
if grep -qE '^  version: "0\.0\.0-dev"' "$SKILL"; then
  echo "error: version placeholder not replaced in SKILL.md" >&2
  exit 1
fi

mkdir -p dist
rm -f "$OUT"
( cd "$STAGE" && zip -qr - course-maker ) > "$OUT"

echo "Built $OUT (version: ${VERSION})"
