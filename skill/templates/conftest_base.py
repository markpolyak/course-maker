# conftest_base.py — BASE TEMPLATE. Used as reference on Stage 2.
#
# IMPORTANT: Replace this placeholder with the actual conftest.py from Lab 1.
# Path to obtain it: ask the professor for the current conftest.py from any real lab.
#
# Structure this file must have:
# ─ Top section (DO NOT TOUCH in any lab):
#   class DummyIPython, get_ipython, fake_input, fake_display, builtins patching
#
# ─ Bottom section (UPDATE per lab):
#   # ======== СИСТЕМА ПОДСЧЁТА БАЛЛОВ ДЛЯ ЛАБОРАТОРНОЙ РАБОТЫ ========
#   TEST_POINTS = { 'test_name': points, ... }
#   TEST_BLOCKS = { 'TestClassName': 'test_name', ... }
#   DATASETS = [...]   ← from Block 0 of exercises.ipynb
#   student_module fixture
#   pytest_runtest_makereport
#   pytest_sessionfinish   ← update only: lab title, bonus presence
#
# Critical invariants (MUST be present verbatim):
#   dataset_id = (Student_ID - 1) % len(DATASETS)
#   print(f"  TASKID is {dataset_id + 1}")
#   print(f"  ПРЕДВАРИТЕЛЬНАЯ ОЦЕНКА В ЖУРНАЛ: ...")
#
# These lines are read by external CI grading systems.
# Any change breaks grading for all students of all labs past and future.

import sys
import types
import io

# ─────────────────────────────────────────────────────────────
# IPython / display mocking — DO NOT TOUCH
# ─────────────────────────────────────────────────────────────

# PLACEHOLDER: paste the full top section from the real conftest.py here.
# Example structure:

# class DummyIPython:
#     ...
#
# def get_ipython():
#     ...
#
# def fake_input(prompt=''):
#     ...
#
# def fake_display(*args, **kwargs):
#     ...
#
# import builtins
# builtins.input = fake_input
# ... (builtins patching)

# ─────────────────────────────────────────────────────────────
# ======== СИСТЕМА ПОДСЧЁТА БАЛЛОВ ДЛЯ ЛАБОРАТОРНОЙ РАБОТЫ ========
# Update this section for each lab.
# ─────────────────────────────────────────────────────────────

TEST_POINTS = {
    # 'test_function_name': points,
    # Example:
    # 'test_data_loaded': 5,
    # 'test_observations_shape': 10,
}

TEST_BLOCKS = {
    # 'TestClassName': 'test_function_name_in_that_class',
    # Example:
    # 'TestTask1_DataLoading': 'test_data_loaded',
}

DATASETS = [
    # Paste from Block 0 of exercises.ipynb.
    # Must match exactly.
    # Example:
    # ('sp500', 'S&P 500 Index, ticker ^GSPC, 2010-2023, yfinance', '^GSPC'),
]

# ─────────────────────────────────────────────────────────────
# student_module fixture — DO NOT TOUCH logic, only DATASETS above
# ─────────────────────────────────────────────────────────────

# PLACEHOLDER: paste student_module fixture from the real conftest.py here.
# import_student_notebook function must be present above it.

# ─────────────────────────────────────────────────────────────
# pytest hooks — see update rules above
# ─────────────────────────────────────────────────────────────

# PLACEHOLDER: paste pytest_runtest_makereport and pytest_sessionfinish here.
#
# pytest_sessionfinish MUST contain:
#   dataset_id = (Student_ID - 1) % len(DATASETS)
#   print(f"  TASKID is {dataset_id + 1}")
#   print(f"  ПРЕДВАРИТЕЛЬНАЯ ОЦЕНКА В ЖУРНАЛ: ...")
