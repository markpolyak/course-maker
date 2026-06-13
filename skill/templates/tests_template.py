"""Style and structure reference for lab tests.py files.

Contains one example of each test pattern. The /course-maker lab tests step
uses this file as a pattern reference — copy structure, not logic. The
actual checks come from lab_spec.md.

Conventions:
- One class per task from lab_spec.md (class name: TestTask{N}_{purpose})
- The student_module fixture is provided by conftest.py (scope='session');
  do not import the student notebook directly
- Bonus tests skip via pytest.skip when the bonus variable is not defined
- Test function names MUST match the keys in TEST_POINTS in conftest.py
- Error messages: in the course language (see course_conventions.md);
  specific (expected vs received)

Localization note:
The strings in this file (docstrings, assertion messages) are English —
they are pattern references only, and are rewritten in the course language
when generating per-lab tests.py. Class and method names always stay in
English.
"""

import os

import numpy as np
import pandas as pd
import pytest


# ===========================================================================
# Pattern 1: variable test
# ===========================================================================

class TestVariableExample:
    """Example: check a DataFrame variable."""

    def test_df_loaded(self, student_module):
        """Variable defined, is a DataFrame, not empty."""
        assert hasattr(student_module, "df"), \
            "Variable `df` is not defined"
        assert student_module.df is not None, \
            "Variable `df` is None"
        assert isinstance(student_module.df, pd.DataFrame), \
            "`df` must be a pandas DataFrame"
        assert len(student_module.df) > 0, \
            "`df` must not be empty"

    def test_df_no_nan(self, student_module):
        """DataFrame contains no missing values."""
        assert student_module.df.isnull().sum().sum() == 0, \
            "`df` contains missing values (NaN)"

    def test_array_shape(self, student_module):
        """Example: check numpy array shape."""
        arr = student_module.observations
        assert isinstance(arr, np.ndarray), \
            "`observations` must be a numpy ndarray"
        assert arr.ndim == 2, \
            f"`observations` must be 2-dimensional, got ndim={arr.ndim}"
        assert arr.shape[1] == 1, \
            f"`observations` must have shape (n, 1), got shape={arr.shape}"
        assert not np.isnan(arr).any(), \
            "`observations` contains NaN values"


# ===========================================================================
# Pattern 2: function test
# ===========================================================================

class TestFunctionExample:
    """Example: check a function that returns a computed result."""

    def test_function_returns_correct_type(self, student_module):
        """Function returns the correct type."""
        func = getattr(student_module, "compute_something", None)
        assert func is not None, "Function `compute_something` is not defined"

        result = func(np.array([1.0, 2.0, 3.0]))
        assert isinstance(result, np.ndarray), \
            f"`compute_something` must return np.ndarray, got {type(result)}"

    def test_function_output_shape(self, student_module):
        """Function output has the correct shape."""
        func = student_module.compute_something
        x = np.array([1.0, 2.0, 3.0])
        result = func(x)
        assert result.shape == x.shape, \
            f"Expected shape {x.shape}, got {result.shape}"

    def test_function_output_values(self, student_module):
        """Function output is correct for a known input."""
        func = student_module.compute_something
        x = np.array([1.0, 2.0, 3.0])
        result = func(x)
        expected = np.array([...])  # fill in expected values per lab_spec.md
        assert np.allclose(result, expected, rtol=0.05), \
            f"Values do not match: expected {expected}, got {result}"

    def test_function_returns_figure(self, student_module):
        """Example: check a function that returns a matplotlib figure."""
        import matplotlib
        func = getattr(student_module, "plot_something", None)
        assert func is not None, "Function `plot_something` is not defined"

        try:
            fig = func(np.array([1.0, 2.0, 3.0]))
        except Exception as e:
            pytest.fail(f"`plot_something` raised: {e}")

        assert isinstance(fig, matplotlib.figure.Figure), \
            f"`plot_something` must return matplotlib.figure.Figure, got {type(fig)}"


# ===========================================================================
# Pattern 3: class test
# ===========================================================================

class TestClassExample:
    """Example: check a user-defined class."""

    def test_class_exists(self, student_module):
        """Class is defined."""
        assert hasattr(student_module, "CustomClass"), \
            "Class `CustomClass` is not defined"

    def test_class_attributes(self, student_module):
        """Instance has the required attributes."""
        CustomClass = student_module.CustomClass
        # Test inputs from lab_spec.md
        params = [np.ones((2, 1)), np.zeros(1)]
        obj = CustomClass(params, lr=0.01)

        assert hasattr(obj, "lr"), "`CustomClass` has no attribute `lr`"
        assert obj.lr > 0, "Attribute `lr` must be > 0"

    def test_class_method_mutates_state(self, student_module):
        """Method updates object state in place."""
        CustomClass = student_module.CustomClass
        W = np.ones((2, 1))
        b = np.zeros(1)
        params = [W, b]
        obj = CustomClass(params, lr=0.01)

        x_batch = np.array([[1.0, 2.0], [3.0, 4.0]])
        y_batch = np.array([0.5, 1.5])
        w_before = params[0].copy()

        try:
            obj.step(x_batch, y_batch)
        except Exception as e:
            pytest.fail(f"`CustomClass.step()` raised: {e}")

        assert not np.allclose(params[0], w_before), \
            "`step()` did not update parameters. Ensure the update is in place."

    def test_class_method_returns_value(self, student_module):
        """Example: method returns a value of the correct type and shape."""
        CustomClass = student_module.CustomClass
        obj = CustomClass(n_components=3)
        obs = np.random.randn(200, 1)
        obj.fit(obs)

        result = obj.decode(obs)
        assert isinstance(result, np.ndarray), \
            f"`decode()` must return np.ndarray, got {type(result)}"
        assert len(result) == len(obs), \
            f"Result length {len(result)} does not match input length {len(obs)}"
        assert result.min() >= 0 and result.max() < 3, \
            "`decode()` values must be in [0, n_components - 1]"


# ===========================================================================
# Pattern 4: artifact test
# ===========================================================================

class TestArtifactExample:
    """Example: check a file artifact saved by the student."""

    def test_artifact_exists(self):
        """Artifact file exists."""
        assert os.path.exists("artifact.json"), \
            "File `artifact.json` not found. Make sure you saved the artifact."

    def test_artifact_loads(self):
        """Artifact loads without error."""
        import json
        try:
            with open("artifact.json") as f:
                json.load(f)
        except Exception as e:
            pytest.fail(f"Failed to load `artifact.json`: {e}")

    def test_artifact_structure(self):
        """Artifact contains the required keys."""
        import json
        with open("artifact.json") as f:
            data = json.load(f)
        required_keys = ["metric1", "metric2", "n_params"]
        for key in required_keys:
            assert key in data, f"Missing key `{key}` in `artifact.json`"

    def test_artifact_values(self):
        """Numerical values in the artifact are correct."""
        import json
        with open("artifact.json") as f:
            data = json.load(f)
        assert data["metric1"] > 0, "`metric1` must be positive"
        # Numerical equality with rtol=0.05
        expected = 42.0  # fill in expected value per lab_spec.md
        assert abs(data["metric2"] - expected) < 0.05 * abs(expected), \
            f"`metric2`: expected ~{expected}, got {data['metric2']}"


# ===========================================================================
# Pattern 5: bonus tasks
#
# Rule: one class per bonus task — same as for regular tasks.
# Do NOT use a single combined TestBonus class.
# Class naming: TestBonus1, TestBonus2, ... (or by task name).
# Each test begins with an existence check and pytest.skip.
# ===========================================================================

class TestBonus1:
    """[Bonus *] Example bonus task with a variable."""

    def test_bonus_variable_exists(self, student_module):
        """[Bonus *] Variable defined and not None."""
        if not hasattr(student_module, "bonus_result") \
                or student_module.bonus_result is None:
            pytest.skip("Bonus task * not completed")
        assert isinstance(student_module.bonus_result, np.ndarray), \
            "`bonus_result` must be np.ndarray"

    def test_bonus_variable_values(self, student_module):
        """[Bonus *] Variable values are correct."""
        if not hasattr(student_module, "bonus_result") \
                or student_module.bonus_result is None:
            pytest.skip("Bonus task * not completed")
        assert len(student_module.bonus_result) > 0, \
            "`bonus_result` must not be empty"


class TestBonus2:
    """[Bonus **] Example bonus task with a function."""

    def test_bonus_function_exists(self, student_module):
        """[Bonus **] Function is defined."""
        if not hasattr(student_module, "bonus_func") \
                or student_module.bonus_func is None:
            pytest.skip("Bonus task ** not completed")
        assert callable(student_module.bonus_func), \
            "`bonus_func` must be callable"

    def test_bonus_function_output(self, student_module):
        """[Bonus **] Function returns the correct result."""
        if not hasattr(student_module, "bonus_func") \
                or student_module.bonus_func is None:
            pytest.skip("Bonus task ** not completed")
        result = student_module.bonus_func(np.array([1.0, 2.0, 3.0]))
        assert result > 0.8, \
            f"Expected value > 0.8, got {result}"
