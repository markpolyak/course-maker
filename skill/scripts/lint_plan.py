#!/usr/bin/env python3
"""Lint the structural integrity of a course_plan.md file.

Standalone: run from a course root, or pass --root.
    python lint_plan.py
    python lint_plan.py --root /path/to/course

The linter is read-only. It prints one finding per line, followed by an OK
summary. ERROR findings make the command exit with status 1; WARN findings do
not affect the exit status.
"""

import argparse
import re
import sys
from pathlib import Path


SESSION_TYPES = {"Lecture", "Seminar", "Lab", "Quiz", "Homework", "Other"}
COUNT_TYPES = ("Lecture", "Seminar", "Lab", "Quiz")
OVERVIEW_LABELS = {
    "Lecture": "Lectures",
    "Seminar": "Seminars",
    "Lab": "Labs",
    "Quiz": "Quizzes",
}
LECTURE_HEADING = re.compile(r"^###\s+Lecture\s+(\d+)\s+—\s+.+$", re.IGNORECASE)
ESTIMATED_TIME = re.compile(r"^\*\*Estimated time:\*\*", re.IGNORECASE)
NOTE_POINTER = re.compile(r"(?:labs|quizzes)/\S+|\bno\s+pipeline\b", re.IGNORECASE)


def split_row(line):
    """Return the stripped cells in a Markdown table row."""
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator(cells):
    """Return True when cells form a Markdown table separator row."""
    return bool(cells) and all(
        cell and set(cell) <= set("-: ") and "-" in cell for cell in cells
    )


def find_section(lines, name):
    """Return the index of a level-two heading, or None if it is absent."""
    target = "## " + name.lower()
    for index, line in enumerate(lines):
        if line.strip().lower() == target:
            return index
    return None


def section_end(lines, start):
    """Return the first line after a level-two section."""
    for index in range(start + 1, len(lines)):
        if lines[index].strip().startswith("## "):
            return index
    return len(lines)


def parse_sessions(lines, start, end, findings):
    """Parse Session data rows and report malformed table rows."""
    table_started = False
    rows = []
    for line_number in range(start + 1, end + 1):
        if line_number == end:
            break
        line = lines[line_number]
        if not line.strip().startswith("|"):
            continue
        cells = split_row(line)
        if not table_started:
            table_started = True
            continue  # Header row.
        if is_separator(cells):
            continue

        location = f"Sessions line {line_number + 1}"
        if len(cells) != 5:
            findings.append(("ERROR", location, f"expected 5 columns, found {len(cells)}"))
        number = cells[0] if cells else ""
        session_type = cells[2] if len(cells) > 2 else ""
        if not number.isdigit():
            findings.append(("ERROR", location, f"# must be a number, found {number!r}"))
        if session_type not in SESSION_TYPES:
            findings.append(("ERROR", location, f"Type must be one of {', '.join(sorted(SESSION_TYPES))}, found {session_type!r}"))
        rows.append((line_number + 1, cells, number, session_type))
    return rows


def overview_counts(lines, start, end, findings):
    """Read canonical Overview counters, reporting missing or invalid values."""
    text = "\n".join(lines[start + 1:end])
    counts = {}
    for session_type, label in OVERVIEW_LABELS.items():
        match = re.search(rf"\*\*{re.escape(label)}:\*\*\s*(\d+)", text, re.IGNORECASE)
        if match is None:
            findings.append(("ERROR", "Overview", f"missing or invalid {label}: counter"))
        else:
            counts[session_type] = int(match.group(1))
    return counts


def lecture_sections(lines, start, end):
    """Return lecture number -> heading line number for canonical lecture headings."""
    sections = {}
    for index in range(start + 1, end):
        match = LECTURE_HEADING.match(lines[index].strip())
        if match:
            sections.setdefault(int(match.group(1)), index)
    return sections


def todo_sections(lines):
    """Return unique nearest heading names for remaining TODO markers."""
    names = []
    current_heading = "document"
    for line in lines:
        heading = re.match(r"^#{2,3}\s+(.+?)\s*$", line.strip())
        if heading:
            current_heading = heading.group(1)
        if "<!-- TODO" in line:
            if current_heading not in names:
                names.append(current_heading)
    return names


def lint(root):
    """Return a list of (severity, location, message) findings for root."""
    plan = root / "course_plan.md"
    if not plan.exists():
        return [("ERROR", ".", f"course_plan.md not found in {root}")]

    lines = plan.read_text(encoding="utf-8").splitlines()
    findings = []
    overview_start = find_section(lines, "Overview")
    sessions_start = find_section(lines, "Sessions")
    lectures_start = find_section(lines, "Lectures")

    counts = {}
    if overview_start is None:
        findings.append(("ERROR", "Overview", "## Overview section not found"))
    else:
        counts = overview_counts(lines, overview_start, section_end(lines, overview_start), findings)

    rows = []
    if sessions_start is None:
        findings.append(("ERROR", "Sessions", "## Sessions section not found"))
    else:
        rows = parse_sessions(lines, sessions_start, section_end(lines, sessions_start), findings)

    for session_type in COUNT_TYPES:
        actual = sum(1 for _, _, _, kind in rows if kind == session_type)
        if session_type in counts and counts[session_type] != actual:
            findings.append(("ERROR", "Overview", f"{OVERVIEW_LABELS[session_type]}: {counts[session_type]} does not match {actual} {session_type} session rows"))

    lecture_rows = {
        int(number) for _, _, number, kind in rows
        if kind == "Lecture" and number.isdigit()
    }
    sections = {}
    lectures_end = len(lines)
    if lectures_start is None:
        if lecture_rows:
            findings.append(("ERROR", "Lectures", "## Lectures section not found"))
    else:
        lectures_end = section_end(lines, lectures_start)
        sections = lecture_sections(lines, lectures_start, lectures_end)

    for number in sorted(lecture_rows - set(sections)):
        findings.append(("ERROR", "Lectures", f"Lecture {number} session has no matching subsection"))
    for number in sorted(set(sections) - lecture_rows):
        findings.append(("ERROR", "Lectures", f"Lecture {number} subsection has no matching session row"))
    for number, heading_index in sections.items():
        next_heading = next(
            (index for index in range(heading_index + 1, lectures_end)
             if lines[index].strip().startswith("### ")),
            lectures_end,
        )
        if not any(ESTIMATED_TIME.match(lines[index].strip()) for index in range(heading_index + 1, next_heading)):
            findings.append(("WARN", "Lectures", f"Lecture {number} has no **Estimated time:**"))

    for line_number, cells, _, kind in rows:
        if kind in {"Lab", "Quiz"}:
            notes = cells[4] if len(cells) > 4 else ""
            if not NOTE_POINTER.search(notes):
                findings.append(("WARN", f"Sessions line {line_number}", f"{kind} Notes has no labs/, quizzes/, or no pipeline pointer"))

    todos = todo_sections(lines)
    if todos:
        findings.append(("WARN", "course_plan.md", "TODO sections: " + ", ".join(todos)))
    return findings


def main():
    parser = argparse.ArgumentParser(description="Lint course_plan.md structure without modifying it.")
    parser.add_argument("--root", default=".", help="Course root (default: current directory)")
    args = parser.parse_args()

    findings = lint(Path(args.root).resolve())
    for severity, location, message in findings:
        print(f"{severity:<9} {location:<20} — {message}")
    errors = sum(1 for severity, _, _ in findings if severity == "ERROR")
    warnings = sum(1 for severity, _, _ in findings if severity == "WARN")
    print(f"OK        {errors} errors, {warnings} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
