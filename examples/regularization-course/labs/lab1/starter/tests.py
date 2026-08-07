"""tests.py — Lab 1: Comparing Regularization Methods

Autograded against labs/lab1/lab_spec.md (course repo only, not shipped to
students). Student code is accessed exclusively through the `student_module`
fixture provided by conftest.py — do not import the notebook directly here.

grade_reporter: none for this course — plain pytest pass/fail, no
grade_report.py / TEST_POINTS contract to keep in sync.
"""

import matplotlib.figure
import numpy as np
import pytest

RTOL = 0.05
ATOL = 0.05


# ===========================================================================
# Shared fixtures
# ===========================================================================

@pytest.fixture(scope="module")
def synthetic_data():
    """Small, well-conditioned synthetic regression data for closed-form /
    coordinate-descent correctness checks (independent of the real dataset,
    so results are exact and fast to check)."""
    rng = np.random.default_rng(0)
    n, p = 200, 5
    X = rng.normal(size=(n, p))
    true_beta = rng.normal(size=p)
    y = X @ true_beta + 0.1 * rng.normal(size=n)
    return X, y


@pytest.fixture(scope="module")
def train_data(student_module):
    """Block 0's train split, used by the dropout MLP tasks."""
    return student_module.X_train, student_module.y_train


@pytest.fixture(scope="module")
def val_data(student_module):
    """Block 0's validation split, used by the dropout MLP tasks."""
    return student_module.X_val, student_module.y_val


def _main_axes(fig):
    """Axes that are real plot panels, excluding colorbars etc."""
    return [ax for ax in fig.axes if ax.get_subplotspec() is not None]


# ===========================================================================
# Block 0 — Setup (0 points, prerequisite sanity check)
# ===========================================================================

class TestTask0_2Setup:
    """[Block 0, 0 pts] Data loading and preprocessing (prerequisite)."""

    def test_variables_defined(self, student_module):
        for name in ("X_train", "X_val", "X_test", "y_train", "y_val", "y_test"):
            assert hasattr(student_module, name), f"Variable `{name}` is not defined"
            assert getattr(student_module, name) is not None, f"Variable `{name}` is None"

    def test_feature_shapes(self, student_module):
        for name in ("X_train", "X_val", "X_test"):
            X = getattr(student_module, name)
            assert isinstance(X, np.ndarray), f"`{name}` must be a numpy ndarray"
            assert X.ndim == 2 and X.shape[1] == 8, \
                f"`{name}` must have shape (n, 8), got shape={X.shape}"

    def test_target_shapes_match(self, student_module):
        for x_name, y_name in (("X_train", "y_train"), ("X_val", "y_val"), ("X_test", "y_test")):
            X = getattr(student_module, x_name)
            y = getattr(student_module, y_name)
            assert y.shape[0] == X.shape[0], \
                f"`{y_name}` length ({y.shape[0]}) does not match `{x_name}` length ({X.shape[0]})"

    def test_split_proportions(self, student_module):
        n_train = student_module.X_train.shape[0]
        n_val = student_module.X_val.shape[0]
        n_test = student_module.X_test.shape[0]
        n_total = n_train + n_val + n_test
        assert abs(n_train / n_total - 0.6) < 0.03, \
            f"Train split should be ~60% of the data, got {n_train / n_total:.2%}"
        assert abs(n_val / n_total - 0.2) < 0.03, \
            f"Validation split should be ~20% of the data, got {n_val / n_total:.2%}"
        assert abs(n_test / n_total - 0.2) < 0.03, \
            f"Test split should be ~20% of the data, got {n_test / n_total:.2%}"

    def test_train_features_standardized(self, student_module):
        X_train = student_module.X_train
        assert not np.isnan(X_train).any(), "`X_train` contains NaN values"
        means = X_train.mean(axis=0)
        stds = X_train.std(axis=0)
        assert np.all(np.abs(means) < 0.1), \
            f"`X_train` does not look standardized: per-feature means are {means}"
        assert np.all(np.abs(stds - 1) < 0.1), \
            f"`X_train` does not look standardized: per-feature stds are {stds}"


# ===========================================================================
# Block 1 — Ridge Regression (5 points)
# ===========================================================================

class TestTask1_1RidgeFit:
    """[Task 1.1, 2 pts] Ridge regression: closed-form solution."""

    def test_function_exists(self, student_module):
        assert hasattr(student_module, "ridge_fit"), "Function `ridge_fit` is not defined"
        assert callable(student_module.ridge_fit), "`ridge_fit` must be callable"

    def test_output_shape(self, student_module, synthetic_data):
        X, y = synthetic_data
        coefs = student_module.ridge_fit(X, y, lam=1.0)
        assert isinstance(coefs, np.ndarray), \
            f"`ridge_fit` must return np.ndarray, got {type(coefs)}"
        assert coefs.shape == (X.shape[1],), \
            f"`ridge_fit` must return shape ({X.shape[1]},), got {coefs.shape}"

    def test_matches_ols_at_lambda_zero(self, student_module, synthetic_data):
        X, y = synthetic_data
        coefs = student_module.ridge_fit(X, y, lam=0.0)
        expected, *_ = np.linalg.lstsq(X, y, rcond=None)
        assert np.allclose(coefs, expected, rtol=RTOL, atol=ATOL), \
            f"At lam=0, ridge_fit should match OLS. Expected {expected}, got {coefs}"

    def test_shrinkage_is_monotonic(self, student_module, synthetic_data):
        X, y = synthetic_data
        norms = [np.linalg.norm(student_module.ridge_fit(X, y, lam=lam))
                 for lam in (0.0, 1.0, 10.0, 100.0)]
        assert all(norms[i] >= norms[i + 1] - ATOL for i in range(len(norms) - 1)), \
            f"Coefficient norm should shrink as lambda grows, got norms={norms}"


class TestTask1_2RidgePath:
    """[Task 1.2, 2 pts] Ridge shrinkage path + plot."""

    @pytest.fixture(scope="class")
    def lambdas(self):
        return np.logspace(-1, 3, 15)

    def test_functions_exist(self, student_module):
        assert hasattr(student_module, "ridge_shrinkage_path"), \
            "Function `ridge_shrinkage_path` is not defined"
        assert hasattr(student_module, "plot_ridge_path"), \
            "Function `plot_ridge_path` is not defined"

    def test_path_shape(self, student_module, synthetic_data, lambdas):
        X, y = synthetic_data
        path = student_module.ridge_shrinkage_path(X, y, lambdas)
        assert isinstance(path, np.ndarray), \
            f"`ridge_shrinkage_path` must return np.ndarray, got {type(path)}"
        assert path.shape == (len(lambdas), X.shape[1]), \
            f"Expected shape {(len(lambdas), X.shape[1])}, got {path.shape}"

    def test_path_matches_ridge_fit(self, student_module, synthetic_data, lambdas):
        X, y = synthetic_data
        path = student_module.ridge_shrinkage_path(X, y, lambdas)
        for i in (0, len(lambdas) // 2, len(lambdas) - 1):
            expected = student_module.ridge_fit(X, y, lam=lambdas[i])
            assert np.allclose(path[i], expected, rtol=RTOL, atol=ATOL), \
                f"Row {i} of the path does not match ridge_fit(X, y, lambdas[{i}])"

    def test_plot_returns_figure_with_labels(self, student_module, synthetic_data, lambdas):
        X, y = synthetic_data
        path = student_module.ridge_shrinkage_path(X, y, lambdas)
        try:
            fig = student_module.plot_ridge_path(lambdas, path)
        except Exception as e:
            pytest.fail(f"`plot_ridge_path` raised: {e}")
        assert isinstance(fig, matplotlib.figure.Figure), \
            f"`plot_ridge_path` must return matplotlib.figure.Figure, got {type(fig)}"
        axes = _main_axes(fig)
        assert axes, "`plot_ridge_path` figure has no axes"
        ax = axes[0]
        assert ax.get_title() != "", "Plot is missing a title"
        assert ax.get_xlabel() != "", "Plot is missing an x-axis label"
        assert ax.get_ylabel() != "", "Plot is missing a y-axis label"


class TestTask1_3RidgeInterpretation:
    """[Task 1.3, 1 pt] Interpreting the shrinkage pattern."""

    def test_defined_and_nonempty(self, student_module):
        text = getattr(student_module, "ridge_interpretation", None)
        assert text is not None, "`ridge_interpretation` is not defined"
        assert isinstance(text, str), "`ridge_interpretation` must be a string"
        assert text.strip() != "", "`ridge_interpretation` must not be empty"
        assert len(text) > 50, \
            f"`ridge_interpretation` looks too short ({len(text)} chars); write a full sentence or two"


# ===========================================================================
# Block 2 — Lasso Regression (5 points)
# ===========================================================================

class TestTask2_1LassoFit:
    """[Task 2.1, 3 pts] Lasso regression: coordinate descent."""

    def test_function_exists(self, student_module):
        assert hasattr(student_module, "lasso_fit"), "Function `lasso_fit` is not defined"

    def test_output_shape(self, student_module, synthetic_data):
        X, y = synthetic_data
        coefs = student_module.lasso_fit(X, y, lam=1.0)
        assert isinstance(coefs, np.ndarray), \
            f"`lasso_fit` must return np.ndarray, got {type(coefs)}"
        assert coefs.shape == (X.shape[1],), \
            f"`lasso_fit` must return shape ({X.shape[1]},), got {coefs.shape}"

    def test_matches_ridge_at_lambda_zero(self, student_module, synthetic_data):
        X, y = synthetic_data
        lasso_coefs = student_module.lasso_fit(X, y, lam=0.0)
        ridge_coefs = student_module.ridge_fit(X, y, lam=0.0)
        assert np.allclose(lasso_coefs, ridge_coefs, rtol=RTOL, atol=ATOL), \
            "At lam=0, lasso_fit should converge to the same solution as ridge_fit(lam=0) (OLS)"

    def test_large_lambda_shrinks_to_near_zero(self, student_module, synthetic_data):
        X, y = synthetic_data
        coefs = student_module.lasso_fit(X, y, lam=1e4)
        assert np.all(np.abs(coefs) < ATOL), \
            f"With a very large lambda, all coefficients should be ~0, got {coefs}"

    def test_sparsity_increases_with_lambda(self, student_module, synthetic_data):
        X, y = synthetic_data
        counts = [
            int(np.sum(np.abs(student_module.lasso_fit(X, y, lam=lam)) > 1e-8))
            for lam in (0.1, 1.0, 10.0, 100.0)
        ]
        assert counts[-1] <= counts[0], \
            f"Nonzero coefficient count should not increase as lambda grows, got counts={counts}"


class TestTask2_2SparsityPath:
    """[Task 2.2, 1 pt] Sparsity path + plot."""

    @pytest.fixture(scope="class")
    def lambdas(self):
        return np.logspace(-1, 3, 15)

    def test_functions_exist(self, student_module):
        assert hasattr(student_module, "n_nonzero_path"), \
            "Function `n_nonzero_path` is not defined"
        assert hasattr(student_module, "plot_sparsity_comparison"), \
            "Function `plot_sparsity_comparison` is not defined"

    def test_output_shape_and_range(self, student_module, synthetic_data, lambdas):
        X, y = synthetic_data
        counts = np.asarray(student_module.n_nonzero_path(X, y, lambdas))
        assert counts.shape == (len(lambdas),), \
            f"Expected shape ({len(lambdas)},), got {counts.shape}"
        assert np.all(counts >= 0) and np.all(counts <= X.shape[1]), \
            f"Nonzero counts must be in [0, {X.shape[1]}], got {counts}"

    def test_sparsity_endpoints(self, student_module, synthetic_data, lambdas):
        X, y = synthetic_data
        counts = np.asarray(student_module.n_nonzero_path(X, y, lambdas))
        assert counts[-1] <= counts[0], \
            f"Nonzero count at the largest lambda should be <= at the smallest, got {counts[0]} -> {counts[-1]}"

    def test_plot_returns_figure_with_legend(self, student_module, synthetic_data, lambdas):
        X, y = synthetic_data
        ridge_path = student_module.ridge_shrinkage_path(X, y, lambdas)
        lasso_counts = student_module.n_nonzero_path(X, y, lambdas)
        try:
            fig = student_module.plot_sparsity_comparison(lambdas, ridge_path, lasso_counts)
        except Exception as e:
            pytest.fail(f"`plot_sparsity_comparison` raised: {e}")
        assert isinstance(fig, matplotlib.figure.Figure), \
            f"`plot_sparsity_comparison` must return matplotlib.figure.Figure, got {type(fig)}"
        axes = _main_axes(fig)
        ax = axes[0]
        assert ax.get_title() != "", "Plot is missing a title"
        assert ax.get_xlabel() != "", "Plot is missing an x-axis label"
        assert ax.get_ylabel() != "", "Plot is missing a y-axis label"
        assert ax.get_legend() is not None, "Plot is missing a legend distinguishing ridge vs. lasso"


class TestTask2_3LassoInterpretation:
    """[Task 2.3, 1 pt] Interpreting sparsity."""

    def test_defined_and_nonempty(self, student_module):
        text = getattr(student_module, "lasso_interpretation", None)
        assert text is not None, "`lasso_interpretation` is not defined"
        assert isinstance(text, str), "`lasso_interpretation` must be a string"
        assert text.strip() != "", "`lasso_interpretation` must not be empty"
        assert len(text) > 50, \
            f"`lasso_interpretation` looks too short ({len(text)} chars); write a full sentence or two"


# ===========================================================================
# Block 3 — Elastic Net & Cross-Validation (5 points)
# ===========================================================================

class TestTask3_1ElasticNetFit:
    """[Task 3.1, 2 pts] Elastic net: generalizing ridge and lasso."""

    def test_function_exists(self, student_module):
        assert hasattr(student_module, "elastic_net_fit"), \
            "Function `elastic_net_fit` is not defined"

    def test_output_shape(self, student_module, synthetic_data):
        X, y = synthetic_data
        coefs = student_module.elastic_net_fit(X, y, lam1=1.0, lam2=1.0)
        assert isinstance(coefs, np.ndarray), \
            f"`elastic_net_fit` must return np.ndarray, got {type(coefs)}"
        assert coefs.shape == (X.shape[1],), \
            f"`elastic_net_fit` must return shape ({X.shape[1]},), got {coefs.shape}"

    def test_reduces_to_lasso_when_lam2_zero(self, student_module, synthetic_data):
        X, y = synthetic_data
        for lam1 in (0.5, 5.0):
            en_coefs = student_module.elastic_net_fit(X, y, lam1=lam1, lam2=0.0)
            lasso_coefs = student_module.lasso_fit(X, y, lam=lam1)
            assert np.allclose(en_coefs, lasso_coefs, rtol=RTOL, atol=ATOL), \
                f"elastic_net_fit(lam1={lam1}, lam2=0) should match lasso_fit(lam={lam1})"

    def test_does_not_raise_at_zero(self, student_module, synthetic_data):
        X, y = synthetic_data
        try:
            coefs = student_module.elastic_net_fit(X, y, lam1=0.0, lam2=0.0)
        except Exception as e:
            pytest.fail(f"`elastic_net_fit` raised at lam1=lam2=0: {e}")
        assert np.all(np.isfinite(coefs)), "`elastic_net_fit` returned non-finite values"


class TestTask3_2CrossValidation:
    """[Task 3.2, 2 pts] Cross-validation for hyperparameter selection."""

    @pytest.fixture(scope="class")
    def grids(self):
        return np.logspace(-1, 1, 4), np.logspace(-1, 1, 4)

    @pytest.fixture(scope="class")
    def cv_result(self, student_module, synthetic_data, grids):
        X, y = synthetic_data
        lam1_grid, lam2_grid = grids
        return student_module.cv_select_elastic_net(X, y, lam1_grid, lam2_grid, k=3)

    def test_function_exists(self, student_module):
        assert hasattr(student_module, "cv_select_elastic_net"), \
            "Function `cv_select_elastic_net` is not defined"

    def test_returns_three_tuple(self, cv_result):
        assert len(cv_result) == 3, \
            f"`cv_select_elastic_net` must return a 3-tuple, got length {len(cv_result)}"

    def test_selected_lambdas_are_from_grid(self, cv_result, grids):
        best_lam1, best_lam2, _ = cv_result
        lam1_grid, lam2_grid = grids
        assert best_lam1 in lam1_grid, \
            f"best_lam1={best_lam1} is not a member of the provided lam1_grid"
        assert best_lam2 in lam2_grid, \
            f"best_lam2={best_lam2} is not a member of the provided lam2_grid"

    def test_cv_mse_is_finite_positive(self, cv_result):
        _, _, best_cv_mse = cv_result
        assert np.isfinite(best_cv_mse) and best_cv_mse > 0, \
            f"best_cv_mse must be finite and positive, got {best_cv_mse}"


class TestTask3_3CVInterpretation:
    """[Task 3.3, 1 pt] Interpreting the cross-validation result."""

    def test_defined_and_nonempty(self, student_module):
        text = getattr(student_module, "cv_interpretation", None)
        assert text is not None, "`cv_interpretation` is not defined"
        assert isinstance(text, str), "`cv_interpretation` must be a string"
        assert text.strip() != "", "`cv_interpretation` must not be empty"
        assert len(text) > 50, \
            f"`cv_interpretation` looks too short ({len(text)} chars); write a full sentence or two"


# ===========================================================================
# Block 4 — Dropout Neural Network (5 points)
# ===========================================================================

class TestTask4_1MLPForward:
    """[Task 4.1, 2 pts] Forward pass with inverted dropout."""

    @pytest.fixture(scope="class")
    def weights(self):
        rng = np.random.default_rng(0)
        n_features, n_hidden = 5, 8
        return {
            "W1": rng.normal(scale=0.1, size=(n_features, n_hidden)),
            "b1": np.zeros(n_hidden),
            "W2": rng.normal(scale=0.1, size=(n_hidden, 1)),
            "b2": np.zeros(1),
        }

    def test_function_exists(self, student_module):
        assert hasattr(student_module, "mlp_forward"), "Function `mlp_forward` is not defined"

    def test_output_shape(self, student_module, synthetic_data, weights):
        X, _ = synthetic_data
        out = student_module.mlp_forward(X, weights, p_drop=0.3, training=False)
        assert isinstance(out, np.ndarray), \
            f"`mlp_forward` must return np.ndarray, got {type(out)}"
        assert out.shape == (X.shape[0],), \
            f"Expected shape ({X.shape[0]},), got {out.shape}"

    def test_eval_mode_is_deterministic(self, student_module, synthetic_data, weights):
        X, _ = synthetic_data
        out1 = student_module.mlp_forward(X, weights, p_drop=0.3, training=False)
        out2 = student_module.mlp_forward(X, weights, p_drop=0.3, training=False)
        assert np.allclose(out1, out2), \
            "`mlp_forward` with training=False must be deterministic (no dropout masking)"

    def test_zero_dropout_matches_eval_mode(self, student_module, synthetic_data, weights):
        X, _ = synthetic_data
        out_train = student_module.mlp_forward(X, weights, p_drop=0.0, training=True)
        out_eval = student_module.mlp_forward(X, weights, p_drop=0.0, training=False)
        assert np.allclose(out_train, out_eval, rtol=RTOL, atol=ATOL), \
            "With p_drop=0.0, training=True and training=False should match (nothing is dropped)"

    def test_training_mode_is_stochastic(self, student_module, synthetic_data, weights):
        X, _ = synthetic_data
        out1 = student_module.mlp_forward(X, weights, p_drop=0.5, training=True)
        out2 = student_module.mlp_forward(X, weights, p_drop=0.5, training=True)
        assert not np.allclose(out1, out2), \
            "`mlp_forward` with training=True and p_drop>0 should use a fresh random mask each call"


class TestTask4_2TrainMLP:
    """[Task 4.2, 2 pts] Training loop with dropout."""

    @pytest.fixture(scope="class")
    def history(self, student_module, train_data, val_data):
        X_train, y_train = train_data
        X_val, y_val = val_data
        return student_module.train_mlp(
            X_train, y_train, X_val, y_val,
            n_hidden=16, p_drop=0.3, lr=0.05, n_epochs=100, seed=0,
        )

    def test_functions_exist(self, student_module):
        assert hasattr(student_module, "train_mlp"), "Function `train_mlp` is not defined"
        assert hasattr(student_module, "plot_training_curves"), \
            "Function `plot_training_curves` is not defined"

    def test_history_keys(self, history):
        for key in ("weights", "train_loss", "val_loss"):
            assert key in history, f"`train_mlp` result is missing key `{key}`"

    def test_loss_array_shapes(self, history):
        assert len(history["train_loss"]) == 100, \
            f"`train_loss` should have length 100 (n_epochs), got {len(history['train_loss'])}"
        assert len(history["val_loss"]) == 100, \
            f"`val_loss` should have length 100 (n_epochs), got {len(history['val_loss'])}"

    def test_val_loss_decreases(self, history):
        val_loss = np.asarray(history["val_loss"])
        assert val_loss[-1] < val_loss[0] + ATOL, \
            f"Validation loss should decrease over training: first={val_loss[0]:.4f}, last={val_loss[-1]:.4f}"

    def test_weights_reproduce_val_loss(self, student_module, val_data, history):
        X_val, y_val = val_data
        preds = student_module.mlp_forward(X_val, history["weights"], p_drop=0.3, training=False)
        mse = float(np.mean((y_val - preds) ** 2))
        expected = history["val_loss"][-1]
        assert abs(mse - expected) <= 0.1 * abs(expected) + ATOL, \
            f"Re-evaluating the returned weights gives MSE={mse:.4f}, but val_loss[-1]={expected:.4f}"

    def test_plot_returns_figure_with_legend(self, student_module, history):
        try:
            fig = student_module.plot_training_curves(history)
        except Exception as e:
            pytest.fail(f"`plot_training_curves` raised: {e}")
        assert isinstance(fig, matplotlib.figure.Figure), \
            f"`plot_training_curves` must return matplotlib.figure.Figure, got {type(fig)}"
        axes = _main_axes(fig)
        ax = axes[0]
        assert ax.get_title() != "", "Plot is missing a title"
        assert ax.get_xlabel() != "", "Plot is missing an x-axis label"
        assert ax.get_ylabel() != "", "Plot is missing a y-axis label"
        assert ax.get_legend() is not None, "Plot is missing a legend distinguishing train vs. val loss"


class TestTask4_3DropoutInterpretation:
    """[Task 4.3, 1 pt] Interpreting dropout's effect."""

    def test_defined_and_nonempty(self, student_module):
        text = getattr(student_module, "dropout_interpretation", None)
        assert text is not None, "`dropout_interpretation` is not defined"
        assert isinstance(text, str), "`dropout_interpretation` must be a string"
        assert text.strip() != "", "`dropout_interpretation` must not be empty"
        assert len(text) > 50, \
            f"`dropout_interpretation` looks too short ({len(text)} chars); write a full sentence or two"


# ===========================================================================
# Bonus Block (5 points)
# One class per bonus task, each skips via pytest.skip when not completed.
# ===========================================================================

class TestBonus1EarlyStopping:
    """[Bonus, Task 5.1, 3 pts] Early stopping with dropout."""

    @pytest.fixture(scope="class")
    def es_history(self, student_module, train_data, val_data):
        if not hasattr(student_module, "train_mlp_early_stopping"):
            pytest.skip("Bonus task 5.1 not completed (train_mlp_early_stopping not defined)")
        X_train, y_train = train_data
        X_val, y_val = val_data
        try:
            result = student_module.train_mlp_early_stopping(
                X_train, y_train, X_val, y_val,
                n_hidden=16, p_drop=0.3, lr=0.05, n_epochs=200, patience=10, seed=0,
            )
        except NotImplementedError:
            pytest.skip("Bonus task 5.1 not completed (raises NotImplementedError)")
        if result is None:
            pytest.skip("Bonus task 5.1 not completed")
        return result

    def test_result_keys(self, es_history):
        for key in ("weights", "train_loss", "val_loss", "stopped_epoch", "best_weights"):
            assert key in es_history, f"[Bonus] Result is missing key `{key}`"

    def test_stopped_epoch_within_bounds(self, es_history):
        assert es_history["stopped_epoch"] <= 200, \
            f"[Bonus] stopped_epoch ({es_history['stopped_epoch']}) exceeds n_epochs=200"

    def test_val_loss_length_matches_stopped_epoch(self, es_history):
        n = len(es_history["val_loss"])
        stopped = es_history["stopped_epoch"]
        assert n in (stopped, stopped + 1), \
            f"[Bonus] len(val_loss)={n} does not match stopped_epoch={stopped} (or stopped_epoch+1)"

    def test_best_weights_at_least_as_good_as_last(self, student_module, val_data, es_history):
        X_val, y_val = val_data
        preds = student_module.mlp_forward(X_val, es_history["best_weights"], p_drop=0.3, training=False)
        best_mse = float(np.mean((y_val - preds) ** 2))
        last_val_loss = es_history["val_loss"][-1]
        assert best_mse <= last_val_loss + ATOL, \
            f"[Bonus] best_weights MSE ({best_mse:.4f}) should be <= the last epoch's val_loss ({last_val_loss:.4f})"


class TestBonus2DropoutSweep:
    """[Bonus, Task 5.2, 2 pts] Sweeping the dropout rate."""

    @pytest.fixture(scope="class")
    def sweep_result(self, student_module, train_data, val_data):
        if not hasattr(student_module, "dropout_rate_sweep_fn"):
            pytest.skip("Bonus task 5.2 not completed (dropout_rate_sweep_fn not defined)")
        X_train, y_train = train_data
        X_val, y_val = val_data
        p_drop_grid = np.linspace(0.0, 0.6, 4)
        try:
            values = student_module.dropout_rate_sweep_fn(
                X_train, y_train, X_val, y_val, p_drop_grid,
                n_hidden=16, lr=0.05, n_epochs=80, seed=0,
            )
        except NotImplementedError:
            pytest.skip("Bonus task 5.2 not completed (raises NotImplementedError)")
        if values is None:
            pytest.skip("Bonus task 5.2 not completed")
        return p_drop_grid, values

    def test_output_shape(self, sweep_result):
        p_drop_grid, values = sweep_result
        values = np.asarray(values)
        assert values.shape == (len(p_drop_grid),), \
            f"[Bonus] Expected shape ({len(p_drop_grid)},), got {values.shape}"

    def test_values_finite_positive(self, sweep_result):
        _, values = sweep_result
        values = np.asarray(values)
        assert np.all(np.isfinite(values)) and np.all(values > 0), \
            f"[Bonus] All MSE values must be finite and positive, got {values}"

    def test_plot_returns_figure(self, student_module, sweep_result):
        p_drop_grid, values = sweep_result
        if not hasattr(student_module, "plot_dropout_sweep"):
            pytest.skip("Bonus task 5.2 plot not completed (plot_dropout_sweep not defined)")
        try:
            fig = student_module.plot_dropout_sweep(p_drop_grid, values)
        except NotImplementedError:
            pytest.skip("Bonus task 5.2 plot not completed")
        except Exception as e:
            pytest.fail(f"[Bonus] `plot_dropout_sweep` raised: {e}")
        assert isinstance(fig, matplotlib.figure.Figure), \
            f"[Bonus] `plot_dropout_sweep` must return matplotlib.figure.Figure, got {type(fig)}"
        axes = _main_axes(fig)
        ax = axes[0]
        assert ax.get_title() != "", "[Bonus] Plot is missing a title"
        assert ax.get_xlabel() != "", "[Bonus] Plot is missing an x-axis label"
        assert ax.get_ylabel() != "", "[Bonus] Plot is missing a y-axis label"
