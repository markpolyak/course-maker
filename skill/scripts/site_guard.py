#!/usr/bin/env python3
"""
site_guard.py — mechanical safety parts of `/course-maker site`.

Publishing is irreversible enough that the two steps protecting instructor-only
material must not depend on an agent having read the workflow. Both live here:

    strip-notes <deck.qmd> <out.qmd>
        Write a copy of the deck with every injected speaker-notes block
        removed. Injected blocks are the ones `/course-maker notes N inject`
        marks with `<!-- course-maker:notes NN -->`. A `::: {.notes}` block
        without a marker is hand-written: removing it would be guesswork, so
        this fails instead.

    check <site-dir>
        Scan a built site for instructor-only content. Exit 1 on any finding.

Patterns here are deliberately narrow. A guard that cries wolf on legitimate
content (a checkmark on a lecture slide, the word "rubric" in a syllabus) gets
loosened by whoever hits the false positive, and then it protects nothing. Every
pattern below is a machine-written marker or a filename, never prose.

Exit codes: 0 clean, 1 findings (or a hand-written notes block), 2 usage error.
"""

import argparse
import re
import sys
from pathlib import Path

# Filenames that are instructor-only wherever they appear in a built site.
DENY_FILENAMES = {
    "rubric.md",
    "quiz_questions.md",
    "defense_questions.md",
    "lab_spec.md",
    "tests.py",
    "conftest.py",
    "grade_report.py",
    "speaker_notes.md",
    "history.md",
    "COURSE_STATE.md",
    "lms_adapter.md",
    "AGENTS.md",
    "CLAUDE.md",
    "datasets_info.md",
}

# Machine-written markers. Each is emitted by this pipeline, never typed by a
# lecturer into student-facing prose, so a hit is always a real leak.
DENY_PATTERNS = [
    ("speaker notes marker", re.compile(r"course-maker:notes")),
    ("rendered speaker notes", re.compile(r"<aside[^>]*class=\"[^\"]*\bnotes\b")),
    ("instructor aside", re.compile(r"<!--\s*instructor")),
    ("rubric metadata", re.compile(r"<!--\s*rubric_in_handout")),
]

TEXT_SUFFIXES = {".html", ".md", ".qmd", ".txt", ".json", ".xml", ".js", ".css"}

NOTES_MARKER = re.compile(r"^\s*<!--\s*course-maker:notes\b[^>]*-->\s*$")
NOTES_OPEN = re.compile(r"^\s*:::+\s*\{\s*\.notes[^}]*\}\s*$")
FENCE_CLOSE = re.compile(r"^\s*:::+\s*$")


def strip_notes(text):
    """
    Remove every marked speaker-notes block. Returns (clean_text, leftovers)
    where leftovers is a list of 1-based line numbers of unmarked `::: {.notes}`
    blocks — those are hand-written and are not touched.
    """
    lines = text.splitlines(keepends=True)
    out = []
    i = 0
    while i < len(lines):
        if NOTES_MARKER.match(lines[i]):
            j = i + 1
            # Allow blank lines between the marker and its div.
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and NOTES_OPEN.match(lines[j]):
                depth = 1
                j += 1
                while j < len(lines) and depth:
                    if NOTES_OPEN.match(lines[j]) or re.match(r"^\s*:::+\s*\{", lines[j]):
                        depth += 1
                    elif FENCE_CLOSE.match(lines[j]):
                        depth -= 1
                    j += 1
                # Swallow one trailing blank line so stripping leaves no gap.
                if j < len(lines) and lines[j].strip() == "":
                    j += 1
                i = j
                continue
        out.append(lines[i])
        i += 1

    clean = "".join(out)
    leftovers = [n for n, ln in enumerate(clean.splitlines(), 1) if NOTES_OPEN.match(ln)]
    return clean, leftovers


def cmd_strip_notes(args):
    src = Path(args.deck)
    if not src.is_file():
        print(f"ERROR deck not found: {src}", file=sys.stderr)
        return 2

    clean, leftovers = strip_notes(src.read_text(encoding="utf-8"))
    if leftovers:
        print(
            f"ERROR {src}: {len(leftovers)} hand-written ::: {{.notes}} block(s) at "
            f"line(s) {', '.join(map(str, leftovers))}.\n"
            "They carry no course-maker marker, so they cannot be removed "
            "automatically without guessing. Delete them, or move the text into "
            "speaker_notes.md and re-run `/course-maker notes N inject`.",
            file=sys.stderr,
        )
        return 1

    Path(args.output).write_text(clean, encoding="utf-8")
    print(f"OK wrote {args.output} (notes stripped)")
    return 0


def cmd_check(args):
    root = Path(args.site_dir)
    if not root.is_dir():
        print(f"ERROR site directory not found: {root}", file=sys.stderr)
        return 2

    findings = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root)
        if path.name in DENY_FILENAMES:
            findings.append(f"LEAK {rel}: instructor-only file present in the built site")
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"SKIP {rel}: {exc}")
            continue
        for label, pattern in DENY_PATTERNS:
            hit = pattern.search(text)
            if hit:
                line = text.count("\n", 0, hit.start()) + 1
                findings.append(f"LEAK {rel}:{line}: {label}")

    for f in findings:
        print(f)
    if findings:
        print(f"\n{len(findings)} finding(s) — do not publish.")
        print(
            "Fix the staging so the content never reaches the site. Do not "
            "narrow these patterns to make the check pass."
        )
        return 1

    print(f"OK no instructor-only content found under {root}")
    print(
        "This checks machine-written markers and filenames only. It cannot judge "
        "whether a page's prose belongs to students — that stays your call."
    )
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    sub = parser.add_subparsers(dest="command", required=True)

    p_strip = sub.add_parser("strip-notes", help="write a deck copy without injected notes")
    p_strip.add_argument("deck")
    p_strip.add_argument("output")
    p_strip.set_defaults(func=cmd_strip_notes)

    p_check = sub.add_parser("check", help="scan a built site for instructor-only content")
    p_check.add_argument("site_dir")
    p_check.set_defaults(func=cmd_check)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
