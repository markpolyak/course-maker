"""Grade reporter: human- and CI-readable scoring block.

OPT-IN extension. Copied into a lab's starter/ as `grade_report.py` when the
course sets `grade_reporter: scoring_ci` (see ../README.md and
skill/references/lab_course_init.md). The universal conftest.py calls
`report(outcomes)` at session end; this reporter turns the outcomes into a
points summary and a grade line.

What is customizable, and where:
  - Labels (SCORING_HEADER, TASKID_LABEL, GRADE_OUTPUT_LABEL): set per course /
    language. If an external CI greps the grade line for an exact phrase, set
    GRADE_OUTPUT_LABEL to that phrase. Change labels, not the print() layout,
    unless the CI agrees.
  - Per-lab data (TEST_POINTS, TEST_BLOCKS, DATASETS): filled by
    /course-maker lab tests N from lab_spec.md.

Variants: the TASKID line is printed only when DATASETS is non-empty, i.e. when
the lab uses the per-student variant extension (skill/extensions/variants/).
A lab can use this reporter with no variants (leave DATASETS empty) or use
variants with a different reporter; the two extensions are independent.
"""

import os


# ── Customizable labels (per course / language) ──────────────────────────────
SCORING_HEADER = "LAB SCORING SYSTEM"
TASKID_LABEL = "TASKID"
GRADE_OUTPUT_LABEL = "PRELIMINARY GRADE"


# ── Per-lab scoring data — filled by /course-maker lab tests N ───────────────
TEST_POINTS: dict[str, int] = {
    # Map: test function name → points awarded if the test passes.
    # Sum should equal the mandatory points total in lab_spec.md (no bonus).
    #
    # Example:
    # "test_data_loaded": 5,
    # "test_model_fit": 15,
}

TEST_BLOCKS: dict[str, str] = {
    # Map: TestClass name → primary test function name in that class.
    # Used to print per-block status.
    #
    # Example:
    # "TestTask1_DataLoading": "test_data_loaded",
    # "TestTask2_ModelFit":   "test_model_fit",
}

DATASETS: list = [
    # Per-student variants only. Paste verbatim from Block 0 of exercises.ipynb;
    # must match exactly. Leave empty if the lab has no variants — the TASKID
    # line is then omitted. See skill/extensions/variants/README.md.
    #
    # Example:
    # ("sp500", "S&P 500 Index, ^GSPC, 2010-2023, yfinance", "^GSPC"),
]


def report(outcomes: dict) -> None:
    """Print the scoring block. `outcomes` maps test name -> outcome string."""
    mandatory_earned = sum(
        pts for name, pts in TEST_POINTS.items()
        if outcomes.get(name) == "passed"
    )
    mandatory_total = sum(TEST_POINTS.values())

    # Bonus convention: tests named test_bonus_*; points from TEST_POINTS or 1.
    bonus_earned = 0
    bonus_total = 0
    for name, outcome in outcomes.items():
        if name.startswith("test_bonus_"):
            pts = TEST_POINTS.get(name, 1)
            bonus_total += pts
            if outcome == "passed":
                bonus_earned += pts

    print()
    print("=" * 60)
    print(f"  {SCORING_HEADER}")
    print("=" * 60)

    # Variant id — printed only when the lab uses per-student variants.
    # The formula is the canonical variant invariant; keep it verbatim when
    # variants are in use. See skill/extensions/variants/README.md.
    if DATASETS:
        try:
            student_id = int(os.environ.get("STUDENT_ID", "1"))
        except ValueError:
            student_id = 1
        dataset_id = (student_id - 1) % len(DATASETS)
        print(f"  {TASKID_LABEL} is {dataset_id + 1}")

    for cls_name, primary_test in TEST_BLOCKS.items():
        outcome = outcomes.get(primary_test, "not_run")
        marker = {"passed": "✓", "failed": "✗", "skipped": "○"}.get(outcome, "?")
        print(f"  {marker} {cls_name}: {outcome}")

    print()
    if bonus_total > 0:
        print(
            f"  {GRADE_OUTPUT_LABEL}: "
            f"{mandatory_earned + bonus_earned} / {mandatory_total} "
            f"(+ {bonus_earned} bonus of {bonus_total})"
        )
    else:
        print(f"  {GRADE_OUTPUT_LABEL}: {mandatory_earned} / {mandatory_total}")
    print("=" * 60)
