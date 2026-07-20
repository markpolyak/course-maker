#!/usr/bin/env python3
"""
validate_state.py — facts layer for `/course-maker doctor`.

Cross-checks the status table in COURSE_STATE.md against artifacts that should
exist on disk, and reports mismatches. This is the deterministic, re-runnable
"facts" engine; the semantic judgement (what to do about each finding) lives in
the doctor command instructions.

Standalone: run from a course root, or pass --root.
    python validate_state.py
    python validate_state.py --root /path/to/course

Output is one finding per line, prefixed by severity:
    DRIFT     — status says done (✅) but the artifact is missing
    STALE     — artifact exists but is older than its source (figures)
    UNTRACKED — artifact exists but the status is not-started (❌)
    BULKY     — a history.md has grown past HISTORY_WARN_LINES (advisory)
    SKIP      — a table row could not be parsed (malformed Markdown)
The final line is an OK summary.

Exit code: 1 if any DRIFT or STALE finding; 0 otherwise. UNTRACKED, BULKY, and
SKIP do not fail the run, so the script is safe to wire into external CI as a
guard.

Source of truth for the status-table format and the step -> file mapping is
references/repository_layout.md. The parser here is deliberately lenient about
column order and spacing, but the set of known step columns and the file each
maps to is encoded below — keep it in sync with repository_layout.md.
"""

import argparse
import sys
from pathlib import Path

DONE = "✅"
NOT_STARTED = "❌"
STATUS_MARKS = ("✅", "🔄", "❌", "⚠️")

# A per-unit history.md above this many lines gets an advisory BULKY finding.
# history.md is append-only anti-repeat memory read in full at the start of every
# step; there is no compaction command, so this is a nudge to trim old *resolved*
# iterations by hand — keeping every rejection/feedback verbatim. Set well above
# a normally iterated unit (~60–80 lines) to avoid noise.
HISTORY_WARN_LINES = 200

# Lecture step column -> path (relative to lectures/<id>/) that must exist when
# the step is marked done. "figures" and "slides" are special-cased below
# (figures: directory + staleness; slides: either slides.tex or slides.md).
LECTURE_FILE_STEPS = {
    "plan": "plan.md",
    "visuals": "visuals.md",
    "notes": "speaker_notes.md",
}

# A done "slides" step is satisfied by either format's deck file.
SLIDES_FILES = ("slides.tex", "slides.md")

# Lab step column -> list of paths (relative to <LAB_DIR>/) that must exist.
# plan/validated/published are process states with no single artifact, so they
# are not file-checked here.
LAB_FILE_STEPS = {
    "spec": ["lab_spec.md"],
    "notebook": ["starter/exercises.ipynb"],
    "tests": ["starter/tests.py", "starter/conftest.py"],
}

# Quiz step column -> path (relative to quizzes/<id>/) that must exist when done.
QUIZ_FILE_STEPS = {
    "plan": "quiz_plan.md",
    "questions": "quiz_questions.md",
    "published": "quiz_student.md",
}

# Homework step column -> path (relative to <HW_DIR>/) that must exist when done.
HOMEWORK_FILE_STEPS = {
    "task": "task.md",
    "rubric": "rubric.md",
    "published": "homework_student.md",
}


def split_row(line):
    """Split a Markdown table row into stripped cells."""
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def is_separator(cells):
    """True for the |---|---| separator row."""
    return all(set(c) <= set("-: ") and "-" in c for c in cells if c != "")


def status_of(cell):
    """Return the status mark in a cell, or None if it holds no known mark."""
    for mark in STATUS_MARKS:
        if mark in cell:
            return mark
    return None


def parse_section(lines, start):
    """
    Parse the first Markdown table after line index `start`.
    Returns (header_cells_lower, rows) where rows are lists of raw cells.
    Lenient: skips blank lines between the heading and the table.
    """
    i = start
    header = None
    rows = []
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("## "):  # next section begins
            break
        if stripped.startswith("|"):
            cells = split_row(line)
            if header is None:
                header = [c.lower() for c in cells]
            elif is_separator(cells):
                pass
            else:
                rows.append(cells)
        i += 1
    return header, rows


def find_section(lines, name):
    """Return the line index of a `## <name>` heading, or None."""
    target = "## " + name.lower()
    for idx, line in enumerate(lines):
        if line.strip().lower() == target:
            return idx
    return None


def all_headings(lines):
    """All `## ...` heading texts present in the file, in order."""
    return [line.strip()[3:].strip() for line in lines if line.strip().startswith("## ")]


def col_index(header, name):
    """Index of the column whose header equals `name`, or None."""
    for idx, col in enumerate(header):
        if col == name:
            return idx
    return None


def cell(row, idx):
    return row[idx] if idx is not None and idx < len(row) else ""


def newest_mtime(paths):
    return max((p.stat().st_mtime for p in paths), default=0.0)


def check_lecture_like(root, subdir, header, rows, findings, extra_steps=None):
    """
    Check a section whose items carry the lecture presentation artifacts
    (plan/visuals/figures/slides/notes), each living in <subdir>/<id>/. Used for
    both `## Lectures` (subdir "lectures") and `## Seminars` (subdir "seminars"):
    a seminar has the same prepared deck as a lecture, plus its own steps passed
    in `extra_steps` (e.g. {"practice": "practice.ipynb"}). Columns the parser
    does not recognize are ignored, not flagged.
    """
    simple_steps = {**LECTURE_FILE_STEPS, **(extra_steps or {})}
    id_idx = col_index(header, "#")
    for row in rows:
        lec_id = cell(row, id_idx).strip()
        if not lec_id:
            findings.append(("SKIP", subdir, "row has no # value"))
            continue
        lec_dir = root / subdir / lec_id
        loc = f"{subdir}/{lec_id}"

        # Simple file-backed steps.
        for step, rel in simple_steps.items():
            idx = col_index(header, step)
            if idx is None:
                continue
            mark = status_of(cell(row, idx))
            target = lec_dir / rel
            if mark == DONE and not target.exists():
                findings.append(("DRIFT", loc, f"{step}: marked ✅ but {rel} is missing"))
            elif mark == NOT_STARTED and target.exists():
                findings.append(("UNTRACKED", loc, f"{step}: {rel} exists but status is ❌"))

        # slides: satisfied by either slides.tex (beamer) or slides.md (slidev).
        slides_idx = col_index(header, "slides")
        if slides_idx is not None:
            mark = status_of(cell(row, slides_idx))
            present = [f for f in SLIDES_FILES if (lec_dir / f).exists()]
            if mark == DONE and not present:
                findings.append(("DRIFT", loc, "slides: marked ✅ but neither slides.tex nor slides.md exists"))
            elif mark == NOT_STARTED and present:
                findings.append(("UNTRACKED", loc, f"slides: {present[0]} exists but status is ❌"))

        # figures: needs at least one PNG, and PNGs must not be older than the script.
        fig_idx = col_index(header, "figures")
        if fig_idx is not None:
            mark = status_of(cell(row, fig_idx))
            fig_dir = lec_dir / "figures"
            pngs = sorted(fig_dir.glob("*.png")) if fig_dir.is_dir() else []
            script = fig_dir / "figures.py"
            if mark == DONE:
                if not pngs:
                    findings.append(("DRIFT", loc, "figures: marked ✅ but no PNG in figures/"))
                elif script.exists() and newest_mtime(pngs) < script.stat().st_mtime:
                    findings.append(("STALE", loc, "figures: PNGs are older than figures.py — re-run it"))
            elif mark == NOT_STARTED and pngs:
                findings.append(("UNTRACKED", loc, "figures: PNGs exist but status is ❌"))


def resolve_lab_dir(root, lab_id, dir_value):
    dir_value = dir_value.strip()
    if dir_value and dir_value not in ("—", "-"):
        return root / "labs" / dir_value
    try:
        n = int(lab_id)
    except ValueError:
        n = lab_id
    return root / "labs" / f"lab{n}"


def check_labs(root, header, rows, findings):
    id_idx = col_index(header, "#")
    dir_idx = col_index(header, "dir")
    for row in rows:
        lab_id = cell(row, id_idx).strip()
        if not lab_id:
            findings.append(("SKIP", "labs", "row has no # value"))
            continue
        lab_dir = resolve_lab_dir(root, lab_id, cell(row, dir_idx))
        loc = str(lab_dir.relative_to(root)) if lab_dir.is_relative_to(root) else str(lab_dir)

        for step, rels in LAB_FILE_STEPS.items():
            idx = col_index(header, step)
            if idx is None:
                continue
            mark = status_of(cell(row, idx))
            if mark == DONE:
                missing = [rel for rel in rels if not (lab_dir / rel).exists()]
                if missing:
                    findings.append(("DRIFT", loc, f"{step}: marked ✅ but missing {', '.join(missing)}"))


def check_quizzes(root, header, rows, findings):
    id_idx = col_index(header, "#")
    for row in rows:
        quiz_id = cell(row, id_idx).strip()
        if not quiz_id:
            findings.append(("SKIP", "quizzes", "row has no # value"))
            continue
        quiz_dir = root / "quizzes" / quiz_id
        loc = f"quizzes/{quiz_id}"
        for step, rel in QUIZ_FILE_STEPS.items():
            idx = col_index(header, step)
            if idx is None:
                continue
            mark = status_of(cell(row, idx))
            if mark != DONE:
                continue
            # "published" is satisfied by the pooled export or any per-variant file.
            if step == "published":
                exported = (quiz_dir / "quiz_student.md").exists() or bool(
                    sorted(quiz_dir.glob("quiz_variant_*.md")))
                if not exported:
                    findings.append(("DRIFT", loc, "published: marked ✅ but no "
                                                   "quiz_student.md or quiz_variant_*.md"))
            elif not (quiz_dir / rel).exists():
                findings.append(("DRIFT", loc, f"{step}: marked ✅ but {rel} is missing"))


def resolve_hw_dir(root, hw_id, dir_value):
    """Homework Dir is a full path from the course root (not a slug under a
    fixed parent, unlike labs), so it can nest under a seminar. Default
    homework/<NN>."""
    dir_value = dir_value.strip()
    if dir_value and dir_value not in ("—", "-"):
        return root / dir_value
    try:
        n = f"{int(hw_id):02d}"
    except ValueError:
        n = hw_id
    return root / "homework" / n


def check_homework(root, header, rows, findings):
    id_idx = col_index(header, "#")
    dir_idx = col_index(header, "dir")
    for row in rows:
        hw_id = cell(row, id_idx).strip()
        if not hw_id:
            findings.append(("SKIP", "homework", "row has no # value"))
            continue
        hw_dir = resolve_hw_dir(root, hw_id, cell(row, dir_idx))
        loc = str(hw_dir.relative_to(root)) if hw_dir.is_relative_to(root) else str(hw_dir)
        for step, rel in HOMEWORK_FILE_STEPS.items():
            idx = col_index(header, step)
            if idx is None:
                continue
            mark = status_of(cell(row, idx))
            if mark == DONE and not (hw_dir / rel).exists():
                findings.append(("DRIFT", loc, f"{step}: marked ✅ but {rel} is missing"))


def check_history_sizes(root, findings):
    """Advisory: flag any history.md that has grown past HISTORY_WARN_LINES.

    Independent of the status table — globs the whole course tree so it catches
    lectures, seminars, labs, and homework (wherever a unit's Dir points). Never
    fails the run; it is a nudge to trim old resolved iterations by hand.
    """
    for path in sorted(root.rglob("history.md")):
        if ".git" in path.parts:
            continue
        n = len(path.read_text(encoding="utf-8").splitlines())
        if n > HISTORY_WARN_LINES:
            loc = str(path.parent.relative_to(root)) if path.is_relative_to(root) else str(path.parent)
            findings.append(("BULKY", loc, f"history.md is {n} lines (> {HISTORY_WARN_LINES}) — "
                                           "consider trimming old resolved iterations (keep rejections verbatim)"))


def main():
    parser = argparse.ArgumentParser(description="Cross-check COURSE_STATE.md against on-disk artifacts.")
    parser.add_argument("--root", default=".", help="Course root (default: current directory)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    state = root / "COURSE_STATE.md"
    if not state.exists():
        print(f"DRIFT     .          — COURSE_STATE.md not found in {root}")
        print("OK        nothing checked")
        return 1

    lines = state.read_text(encoding="utf-8").splitlines()
    findings = []

    n_lectures = 0
    for section, subdir in (("Lectures", "lectures"), ("Seminars", "seminars")):
        start = find_section(lines, section)
        if start is None:
            continue
        header, rows = parse_section(lines, start + 1)
        if header:
            n_lectures += len(rows)
            extra = {"practice": "practice.ipynb"} if subdir == "seminars" else None
            check_lecture_like(root, subdir, header, rows, findings, extra_steps=extra)

    lab_start = find_section(lines, "Labs")
    n_labs = 0
    if lab_start is not None:
        header, rows = parse_section(lines, lab_start + 1)
        if header:
            n_labs = len(rows)
            check_labs(root, header, rows, findings)

    quiz_start = find_section(lines, "Quizzes")
    n_quizzes = 0
    if quiz_start is not None:
        header, rows = parse_section(lines, quiz_start + 1)
        if header:
            n_quizzes = len(rows)
            check_quizzes(root, header, rows, findings)

    hw_start = find_section(lines, "Homework")
    n_homework = 0
    if hw_start is not None:
        header, rows = parse_section(lines, hw_start + 1)
        if header:
            n_homework = len(rows)
            check_homework(root, header, rows, findings)

    check_history_sizes(root, findings)

    # Loud guard against a blind run: if no recognized rows were checked, the
    # status table is empty or uses section headings this script does not know.
    # Reporting a reassuring "OK ... 0 checked" would be a false all-clear — the
    # whole point of the checker is to NOT give false comfort.
    if n_lectures == 0 and n_labs == 0 and n_quizzes == 0 and n_homework == 0:
        headings = all_headings(lines)
        found = ", ".join(headings) if headings else "(no ## sections)"
        print("BLIND     COURSE_STATE.md      — no '## Lectures', '## Seminars', "
              "'## Labs', '## Quizzes', or '## Homework' rows recognized; nothing was checked")
        print(f"          sections present: {found}")
        print("OK        0 items checked; blind run (no false all-clear)")
        return 1

    for severity, loc, msg in findings:
        print(f"{severity:<9} {loc:<20} — {msg}")

    failing = sum(1 for s, _, _ in findings if s in ("DRIFT", "STALE"))
    other = len(findings) - failing
    print(f"OK        {n_lectures} lecture/seminar, {n_labs} labs, {n_quizzes} quizzes, "
          f"{n_homework} homework checked; {failing} drift/stale, {other} other")
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
