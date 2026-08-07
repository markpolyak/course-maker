# lab_spec.md — contract between Stage 1 and Stage 2
# NOT published to students. Stored only in course repo (labs/lab1/).

## Metadata

lab_id: lab1
title: Comparing Regularization Methods
course: Regularization in Machine Learning
theory_md: false
notebook: exercises.ipynb


## Infrastructure

environment: Local Python 3.10+ / GitHub Actions CI (CPU only, no GPU needed — pure numpy)
ci: pytest + GitHub Actions (tests.yaml)
nbconvert: true         # exercises.ipynb → exercises.py via nbconvert
graded_markers: false


## Datasets

# lab_variants: false — single fixed dataset for all students, not per-student.
# Documented here (not in the template's variants section) for Stage 2's benefit.
dataset:
  description: "California housing dataset (sklearn.datasets.fetch_california_housing, source: StatLib)"
  download: "sklearn.datasets.fetch_california_housing() — downloads and caches to ~/scikit_learn_data on first call; requires network access in CI on first run"
  known_issues: null
  expected_shape: "(20640, 8) features, (20640,) target"
  key_columns: [MedInc, HouseAge, AveRooms, AveBedrms, Population, AveOccup, Latitude, Longitude]
  value_range: "target (median house value) in units of $100,000, range ~0.15–5.0"
  normalization: "features standardized (zero mean, unit variance) using train-set statistics only, applied to val/test"


## Tasks

# --- Block 0: Setup (0 points, sanity check only) ---

- id: task_0_2
  block: 0
  title: Load and Prepare the Data
  variable: [X_train, X_val, X_test, y_train, y_val, y_test]
  type: np.ndarray
  points: 0
  bonus: false
  checks:
    - "X_train.shape[1] == 8 and X_val.shape[1] == 8 and X_test.shape[1] == 8"
    - "y_train.shape[0] == X_train.shape[0], same for val/test"
    - "split proportions approximately 60/20/20 (atol=0.03 on each fraction of total n=20640)"
    - "X_train has no NaNs; np.abs(X_train.mean(axis=0)) < 0.1 and np.abs(X_train.std(axis=0) - 1) < 0.1 (train-set standardization)"
  tolerance: "atol=0.1 on standardization checks (numerical, not exact due to ddof choice)"
  notes: >
    Zero points — mandatory technical prerequisite. If this fails, skip
    downstream task tests (module-scope fixture should still attempt them,
    but failures here explain cascading failures elsewhere).

# --- Block 1: Ridge Regression (5 points) ---

- id: task_1_1
  block: 1
  title: "Ridge Regression: Closed-Form Solution"
  function: ridge_fit
  signature: "ridge_fit(X: np.ndarray, y: np.ndarray, lam: float) -> np.ndarray"
  points: 2
  bonus: false
  checks:
    - "returned array has shape (n_features,)"
    - "at lam=0.0, matches np.linalg.lstsq(X, y) coefficients within rtol=0.05"
    - "coefficient L2 norm is non-increasing across lam in [0, 1, 10, 100] on X_train/y_train"
    - "does not raise for a small well-conditioned synthetic X, y"
  tolerance: "rtol=0.05 (model parameters, order of 1)"
  notes: >
    Use X_train/y_train (already standardized/centered) as the test fixture
    input for the shrinkage-monotonicity check.

- id: task_1_2
  block: 1
  title: "Ridge Shrinkage Path"
  function: [ridge_shrinkage_path, plot_ridge_path]
  signature:
    - "ridge_shrinkage_path(X: np.ndarray, y: np.ndarray, lambdas: np.ndarray) -> np.ndarray"
    - "plot_ridge_path(lambdas: np.ndarray, path: np.ndarray) -> matplotlib.figure.Figure"
  points: 2
  bonus: false
  checks:
    - "ridge_shrinkage_path returns shape (len(lambdas), n_features)"
    - "row i of the returned path matches ridge_fit(X, y, lambdas[i]) within rtol=0.05 (spot-check 3 indices: first, middle, last)"
    - "plot_ridge_path returns isinstance(fig, matplotlib.figure.Figure)"
    - "main axes has non-empty title: ax.get_title() != ''"
    - "main axes has non-empty xlabel and ylabel"
  tolerance: "rtol=0.05"
  notes: >
    Matplotlib checks are observable-behavior only (title/labels), per the
    no-internal-object-inspection rule. Do not assert on line count or color.

- id: task_1_3
  block: 1
  title: "Interpreting the Shrinkage Pattern"
  text_var: ridge_interpretation
  points: 1
  bonus: false
  # (also listed under Text Answers below)

# --- Block 2: Lasso Regression (5 points) ---

- id: task_2_1
  block: 2
  title: "Lasso Regression: Coordinate Descent"
  function: lasso_fit
  signature: "lasso_fit(X: np.ndarray, y: np.ndarray, lam: float, max_iter: int = 1000, tol: float = 1e-6) -> np.ndarray"
  points: 3
  bonus: false
  checks:
    - "returned array has shape (n_features,)"
    - "at lam=0.0, matches ridge_fit(X, y, lam=0.0) within rtol=0.05 (coordinate descent converges to OLS)"
    - "at a large lam (lam=1e4 on standardized X_train/y_train), all coefficients ~0 (atol=0.05)"
    - "nonzero coefficient count is non-increasing across lam in [0.1, 1, 10, 100]"
  tolerance: "rtol=0.05 for nonzero comparisons; atol=0.05 near-zero coefficients"
  notes: >
    atol (not rtol) required for the large-lam near-zero check, per the
    tolerance rule for values approaching zero.

- id: task_2_2
  block: 2
  title: "Sparsity Path"
  function: [n_nonzero_path, plot_sparsity_comparison]
  signature:
    - "n_nonzero_path(X: np.ndarray, y: np.ndarray, lambdas: np.ndarray) -> np.ndarray"
    - "plot_sparsity_comparison(lambdas: np.ndarray, ridge_path: np.ndarray, lasso_nonzero_path: np.ndarray) -> matplotlib.figure.Figure"
  points: 1
  bonus: false
  checks:
    - "n_nonzero_path returns shape (len(lambdas),) with integer-compatible values in [0, n_features]"
    - "n_nonzero_path[-1] <= n_nonzero_path[0] (sparsity increases with lambda, allowing the endpoints comparison rather than strict monotonicity)"
    - "plot_sparsity_comparison returns matplotlib.figure.Figure with non-empty title, xlabel, ylabel"
    - "main axes has a legend: ax.get_legend() is not None"
  tolerance: null
  notes: >
    Endpoint comparison (not full monotonicity) avoids false failures from
    coordinate-descent ties near threshold lambdas.

- id: task_2_3
  block: 2
  title: "Interpreting Sparsity"
  text_var: lasso_interpretation
  points: 1
  bonus: false

# --- Block 3: Elastic Net & Cross-Validation (5 points) ---

- id: task_3_1
  block: 3
  title: "Elastic Net: Generalizing Ridge and Lasso"
  function: elastic_net_fit
  signature: "elastic_net_fit(X: np.ndarray, y: np.ndarray, lam1: float, lam2: float, max_iter: int = 1000, tol: float = 1e-6) -> np.ndarray"
  points: 2
  bonus: false
  checks:
    - "returned array has shape (n_features,)"
    - "elastic_net_fit(X, y, lam1, lam2=0.0) matches lasso_fit(X, y, lam1) within rtol=0.05"
    - "does not raise and returns finite values for lam1=lam2=0"
  tolerance: "rtol=0.05"
  notes: >
    Only the lam2=0 boundary is checked against lasso_fit directly (per the
    plan's "generalizes lasso_fit" requirement); no separate closed-form
    ridge-boundary check since coordinate descent at lam1=0 does not reduce
    to the closed-form ridge path exactly under a fixed max_iter/tol.

- id: task_3_2
  block: 3
  title: "Cross-Validation for Hyperparameter Selection"
  function: cv_select_elastic_net
  signature: "cv_select_elastic_net(X: np.ndarray, y: np.ndarray, lam1_grid: np.ndarray, lam2_grid: np.ndarray, k: int = 5) -> tuple"
  points: 2
  bonus: false
  checks:
    - "returns a 3-tuple (best_lam1, best_lam2, best_cv_mse)"
    - "best_lam1 in lam1_grid and best_lam2 in lam2_grid (membership, since grid search)"
    - "best_cv_mse is finite and > 0"
    - "best_cv_mse is reproducible within rtol=0.05 across two calls with the same inputs"
  tolerance: "rtol=0.05"
  notes: >
    Heavy operation (10x10 grid x k=5 folds) — run via a module-scope fixture,
    not repeated per test. Expect ~10-30s runtime in CI.

- id: task_3_3
  block: 3
  title: "Interpreting the Cross-Validation Result"
  text_var: cv_interpretation
  points: 1
  bonus: false

# --- Block 4: Dropout Neural Network (5 points) ---

- id: task_4_1
  block: 4
  title: "Forward Pass with Inverted Dropout"
  function: mlp_forward
  signature: "mlp_forward(X: np.ndarray, weights: dict, p_drop: float, training: bool) -> np.ndarray"
  points: 2
  bonus: false
  checks:
    - "returns np.ndarray of shape (n_samples,)"
    - "training=False is deterministic across repeated calls with the same X/weights"
    - "with p_drop=0.0 and training=True, output matches training=False output within rtol=0.05 (no units dropped, scale factor 1/(1-0)=1)"
    - "with p_drop=0.5 and training=True, two calls on the same X/weights produce different outputs (fresh random mask each call)"
  tolerance: "rtol=0.05"
  notes: >
    Fixed test weights dict (small, deterministic shapes) constructed in the
    test fixture — not the notebook's demo_weights (rng-seeded but not part
    of the graded contract).

- id: task_4_2
  block: 4
  title: "Training Loop with Dropout"
  function: [train_mlp, plot_training_curves]
  signature:
    - "train_mlp(X_train, y_train, X_val, y_val, n_hidden: int, p_drop: float, lr: float, n_epochs: int, seed: int = 0) -> dict"
    - "plot_training_curves(history: dict) -> matplotlib.figure.Figure"
  points: 2
  bonus: false
  checks:
    - "returns dict with keys 'weights', 'train_loss', 'val_loss'"
    - "train_loss and val_loss have shape (n_epochs,)"
    - "val_loss[-1] < val_loss[0] on X_train/y_train/X_val/y_val with n_hidden=16, p_drop=0.3, lr=0.05, n_epochs=100, seed=0 (smaller than the notebook demo for test speed), atol=0.05 slack"
    - "mlp_forward(X_val, weights, p_drop=0.3, training=False) reproduces a val MSE within rtol=0.1 of val_loss[-1]"
    - "plot_training_curves returns matplotlib.figure.Figure with non-empty title, xlabel, ylabel, and a legend"
  tolerance: "atol=0.05 on loss decrease; rtol=0.1 on val-loss reproduction (looser: two independent MSE computations)"
  notes: >
    Test uses smaller n_hidden/n_epochs than the notebook's demo cell to keep
    CI runtime reasonable; behavior (loss decreasing) should still hold.

- id: task_4_3
  block: 4
  title: "Interpreting Dropout's Effect"
  text_var: dropout_interpretation
  points: 1
  bonus: false

# --- Bonus Block (5 points) ---

- id: task_5_1
  block: 5
  title: "Early Stopping with Dropout"
  function: train_mlp_early_stopping
  signature: "train_mlp_early_stopping(X_train, y_train, X_val, y_val, n_hidden: int, p_drop: float, lr: float, n_epochs: int, patience: int, seed: int = 0) -> dict"
  points: 3
  bonus: true
  checks:
    - "returns dict with keys 'weights', 'train_loss', 'val_loss', 'stopped_epoch', 'best_weights'"
    - "stopped_epoch <= n_epochs"
    - "len(val_loss) in {stopped_epoch, stopped_epoch + 1} (off-by-one tolerated depending on indexing convention)"
    - "MSE of mlp_forward(X_val, best_weights, p_drop, training=False) is <= val_loss[-1] + atol=0.05 (best epoch should be at least as good as the last)"
  tolerance: "atol=0.05"
  notes: >
    Bonus. Test skips via pytest.skip if train_mlp_early_stopping is not
    implemented (raises NotImplementedError) or stopped_epoch is None.

- id: task_5_2
  block: 5
  title: "Sweeping the Dropout Rate"
  function: [dropout_rate_sweep_fn, plot_dropout_sweep]
  signature:
    - "dropout_rate_sweep_fn(X_train, y_train, X_val, y_val, p_drop_grid: np.ndarray, n_hidden: int, lr: float, n_epochs: int, seed: int = 0) -> np.ndarray"
    - "plot_dropout_sweep(p_drop_grid: np.ndarray, mse_values: np.ndarray) -> matplotlib.figure.Figure"
  points: 2
  bonus: true
  checks:
    - "dropout_rate_sweep_fn returns np.ndarray of shape (len(p_drop_grid),)"
    - "all returned values are finite and > 0"
    - "plot_dropout_sweep returns matplotlib.figure.Figure with non-empty title, xlabel, ylabel"
  tolerance: null
  notes: >
    Bonus. Test skips via pytest.skip if not implemented.


## Text Answers

text_vars:
  - name: ridge_interpretation
    type: str
    block: 1
    points: 1
    checks:
      - "defined and not None"
      - "not empty string"
      - "length > 50"
  - name: lasso_interpretation
    type: str
    block: 2
    points: 1
    checks:
      - "defined and not None"
      - "not empty string"
      - "length > 50"
  - name: cv_interpretation
    type: str
    block: 3
    points: 1
    checks:
      - "defined and not None"
      - "not empty string"
      - "length > 50"
  - name: dropout_interpretation
    type: str
    block: 4
    points: 1
    checks:
      - "defined and not None"
      - "not empty string"
      - "length > 50"


## Artifacts

artifacts: []


## Scoring Table

| Block | Task | Points | Bonus |
|-------|------|--------|-------|
| 0 | Load and Prepare the Data | 0 | — |
| 1 | Ridge: closed-form (1.1) | 2 | — |
| 1 | Ridge: shrinkage path + plot (1.2) | 2 | — |
| 1 | Ridge: interpretation (1.3) | 1 | — |
| 2 | Lasso: coordinate descent (2.1) | 3 | — |
| 2 | Lasso: sparsity path + plot (2.2) | 1 | — |
| 2 | Lasso: interpretation (2.3) | 1 | — |
| 3 | Elastic net: fit (3.1) | 2 | — |
| 3 | Elastic net: CV selection (3.2) | 2 | — |
| 3 | Elastic net: CV interpretation (3.3) | 1 | — |
| 4 | Dropout: forward pass (4.1) | 2 | — |
| 4 | Dropout: training loop + plot (4.2) | 2 | — |
| 4 | Dropout: interpretation (4.3) | 1 | — |
| 5 | Early stopping + dropout (5.1) | 3 | ✓ |
| 5 | Dropout-rate sweep (5.2) | 2 | ✓ |
| **Total** | | **20 + 5 bonus** | |


## Notes for Stage 2

notes:
  - "conftest.py runs the nbconvert'd exercises.py once per test module (scope='module') via the student_module fixture; all task tests read variables/functions from that fixture rather than re-running the notebook."
  - "grade_reporter: none for this course — tests.py is plain pytest pass/fail, no grade_report.py or TEST_POINTS/TEST_BLOCKS dict needed."
  - "lab_variants: false — single fixed California housing dataset for all students; no DATASET_TYPE branching needed anywhere in tests."
  - "fetch_california_housing() requires network access on first call in CI (caches to ~/scikit_learn_data afterward) — CI runner needs network access, or the cache should be pre-warmed/pinned as a CI artifact."
  - "Tasks 3.2, 4.2, 5.1, 5.2 involve model fitting/training — call them once via module-scope fixtures inside their test classes, not per assertion, to keep CI runtime reasonable (Task 3.2's 10x10 grid x 5-fold CV is the heaviest single call)."
  - "For task_4.2's test, use smaller n_hidden/n_epochs than the notebook's demo cell (n_hidden=16, n_epochs=100 vs. the notebook's 32/300) purely for CI speed; this does not change what students see in the notebook, only the values used inside tests.py."
  - "Always pass seed=0 explicitly in test calls to train_mlp / train_mlp_early_stopping / dropout_rate_sweep_fn for deterministic test outcomes, per the reproducibility rule."
