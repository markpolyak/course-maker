# Lab 1 — Comparing Regularization Methods

**Course:** Regularization in Machine Learning

**Goal:** Implement and compare Ridge, Lasso, and Elastic Net regression, and
dropout in a small neural network, tuning regularization strength via
cross-validation.

## Repository structure

```
starter/
├── exercises.ipynb      # the notebook you complete and submit
├── conftest.py           # test harness (do not modify)
├── tests.py               # the tests your submission is graded against
├── requirements.txt      # pinned dependency versions
├── README.md              # this file
└── .github/workflows/tests.yaml   # CI: runs the tests below on every push
```

## Setup

```bash
pip install -r requirements.txt
jupyter notebook exercises.ipynb
```

The California housing dataset is downloaded automatically on first run via
`sklearn.datasets.fetch_california_housing()` (requires network access the
first time; cached locally afterward).

## Task structure

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

## Running the tests locally

```bash
jupyter nbconvert --to python exercises.ipynb
pytest tests.py -v
```

CI (GitHub Actions, `.github/workflows/tests.yaml`) runs the same command on
every push.

## Submitting

1. Run `Kernel → Restart & Run All` in `exercises.ipynb` and confirm there are
   no errors.
2. Run the self-check cell at the end of the notebook and confirm all
   required variables show ✓.
3. Submit `exercises.ipynb` through the delivery channel announced by your
   instructor.

## Questions?

Reach out to your instructor through the course's usual communication
channel.
