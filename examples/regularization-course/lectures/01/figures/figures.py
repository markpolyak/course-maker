"""
Lecture 1 figures — Regularization Foundations
Generates: fig01_polynomial_fits.png, fig02_train_val_error.png,
           fig03_ridge_shrinkage.png, fig04_l2_geometry.png,
           fig05_l1_geometry.png, fig06_lasso_path_cv.png
Run from the lecture directory: python figures/figures.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# ── Global style ──────────────────────────────────────────────────────────────
mpl.rcParams.update({
    'figure.dpi': 180,
    'font.family': 'serif',
    'font.size': 11,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': False,
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'figure.facecolor': 'white',
})

PALETTE = ['#2E4057', '#E84855', '#F4A261', '#5B8DB8', '#6B9E78']

np.random.seed(42)  # always fix seed


# ── Shared helpers ──────────────────────────────────────────────────────────────

def ridge_fit(X, y, lam):
    """Closed-form ridge solution: (X'X + lam*I)^-1 X'y."""
    p = X.shape[1]
    return np.linalg.solve(X.T @ X + lam * np.eye(p), X.T @ y)


def soft_threshold(rho, lam):
    if rho > lam:
        return rho - lam
    elif rho < -lam:
        return rho + lam
    return 0.0


def lasso_fit(X, y, lam, n_iter=500, tol=1e-9):
    """Coordinate-descent lasso for: minimize 0.5*||y - Xb||^2 + lam*||b||_1."""
    n, p = X.shape
    beta = np.zeros(p)
    col_sq = (X ** 2).sum(axis=0)
    for _ in range(n_iter):
        beta_old = beta.copy()
        for j in range(p):
            if col_sq[j] == 0:
                beta[j] = 0.0
                continue
            residual = y - X @ beta + X[:, j] * beta[j]
            rho = X[:, j] @ residual
            beta[j] = soft_threshold(rho, lam) / col_sq[j]
        if np.max(np.abs(beta - beta_old)) < tol:
            break
    return beta


# ── Figure functions ───────────────────────────────────────────────────────────

def fig01_polynomial_fits():
    """Slide 3: underfit / good fit / overfit on the same noisy dataset."""
    rng = np.random.default_rng(42)
    x = np.linspace(0, 1, 30)
    y_true = np.sin(2 * np.pi * x)
    y = y_true + rng.normal(0, 0.3, size=x.shape)
    x_grid = np.linspace(0, 1, 300)

    degrees = [1, 4, 15]
    titles = ['Degree 1 — underfit', 'Degree 4 — good fit', 'Degree 15 — overfit']

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True)
    for ax, deg, title in zip(axes, degrees, titles):
        with np.errstate(all='ignore'):
            coefs = np.polyfit(x, y, deg)
        y_grid = np.polyval(coefs, x_grid)
        ax.plot(x_grid, np.sin(2 * np.pi * x_grid), color=PALETTE[4],
                 linestyle='--', linewidth=1.2, label='True function')
        ax.plot(x_grid, y_grid, color=PALETTE[1], linewidth=2, label='Fitted polynomial')
        ax.scatter(x, y, color=PALETTE[0], s=22, zorder=3, label='Training data')
        ax.set_title(title, fontsize=11)
        ax.set_xlabel('x')
        ax.set_ylim(-2.2, 2.2)
    axes[0].set_ylabel('y')
    axes[0].legend(loc='upper right', fontsize=7.5, frameon=False)
    fig.tight_layout()
    fig.savefig('figures/fig01_polynomial_fits.png', bbox_inches='tight')
    plt.close(fig)


def fig02_train_val_error():
    """Slide 5: train vs validation error against model complexity."""
    rng = np.random.default_rng(7)
    x = rng.uniform(0, 1, 40)
    x.sort()
    y_true = np.sin(2 * np.pi * x)
    y = y_true + rng.normal(0, 0.3, size=x.shape)

    idx = rng.permutation(len(x))
    train_idx, val_idx = idx[:24], idx[24:]
    x_train, y_train = x[train_idx], y[train_idx]
    x_val, y_val = x[val_idx], y[val_idx]

    degrees = np.arange(1, 16)
    train_errors, val_errors = [], []
    for deg in degrees:
        with np.errstate(all='ignore'):
            coefs = np.polyfit(x_train, y_train, deg)
        train_pred = np.polyval(coefs, x_train)
        val_pred = np.polyval(coefs, x_val)
        train_errors.append(np.mean((y_train - train_pred) ** 2))
        val_errors.append(np.mean((y_val - val_pred) ** 2))
    val_errors = np.clip(val_errors, 0, 5)  # keep runaway high-degree error readable

    best_degree = degrees[int(np.argmin(val_errors))]

    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(degrees, train_errors, color=PALETTE[0], marker='o', markersize=4,
            linewidth=1.8, label='Training error')
    ax.plot(degrees, val_errors, color=PALETTE[1], marker='o', markersize=4,
            linewidth=1.8, label='Validation error')
    ax.axvspan(best_degree + 0.5, degrees[-1] + 0.5, color=PALETTE[1], alpha=0.08)
    ax.text(degrees[-1] - 0.2, ax.get_ylim()[1] * 0.9 if ax.get_ylim()[1] > 0 else 1,
            'overfitting zone', color=PALETTE[1], fontsize=8.5, ha='right', va='top')
    ax.axvline(best_degree, color=PALETTE[4], linestyle='--', linewidth=1)
    ax.set_xlabel('Model complexity (polynomial degree)')
    ax.set_ylabel('Mean squared error')
    ax.set_yscale('log')
    ax.legend(fontsize=9, frameon=False)
    fig.tight_layout()
    fig.savefig('figures/fig02_train_val_error.png', bbox_inches='tight')
    plt.close(fig)


def fig03_ridge_shrinkage():
    """Slide 8: ridge coefficient trajectories vs. lambda."""
    rng = np.random.default_rng(3)
    n, p = 60, 6
    X = rng.normal(size=(n, p))
    X = (X - X.mean(axis=0)) / X.std(axis=0)  # standardize
    beta_true = np.array([3.0, -2.0, 1.5, 0.0, 0.0, 0.8])
    y = X @ beta_true + rng.normal(0, 1.0, size=n)

    lambdas = np.logspace(-2, 3, 100)
    coef_paths = np.array([ridge_fit(X, y, lam) for lam in lambdas])

    fig, ax = plt.subplots(figsize=(6.5, 4))
    colors = [PALETTE[i % len(PALETTE)] for i in range(p)]
    for j in range(p):
        ax.plot(lambdas, coef_paths[:, j], color=colors[j], linewidth=1.8,
                label=f'$\\beta_{{{j+1}}}$')
    ax.axhline(0, color='gray', linewidth=0.7)
    ax.set_xscale('log')
    ax.set_xlabel(r'Regularization strength $\lambda$ (log scale)')
    ax.set_ylabel('Coefficient value')
    ax.legend(fontsize=8, frameon=False, ncol=2, loc='upper right')
    fig.tight_layout()
    fig.savefig('figures/fig03_ridge_shrinkage.png', bbox_inches='tight')
    plt.close(fig)


def fig04_l2_geometry():
    """Slide 9: elliptical loss contours + circular L2 constraint region."""
    rng = np.random.default_rng(11)
    n = 40
    rho = 0.7
    cov = [[1.0, rho], [rho, 1.0]]
    X = rng.multivariate_normal([0, 0], cov, size=n)
    beta_true = np.array([3.0, 2.0])
    y = X @ beta_true + rng.normal(0, 1.0, size=n)

    beta_ols = np.linalg.lstsq(X, y, rcond=None)[0]
    beta_ridge = ridge_fit(X, y, lam=8.0)
    t = np.linalg.norm(beta_ridge)

    b1 = np.linspace(-2, 5, 250)
    b2 = np.linspace(-2, 5, 250)
    B1, B2 = np.meshgrid(b1, b2)
    Z = np.zeros_like(B1)
    for i in range(B1.shape[0]):
        diff = y[:, None] - X[:, [0]] * B1[i, :] - X[:, [1]] * B2[i, :]
        Z[i, :] = (diff ** 2).sum(axis=0)

    theta = np.linspace(0, 2 * np.pi, 200)
    circle_x, circle_y = t * np.cos(theta), t * np.sin(theta)

    lim_lo, lim_hi = -2, 5

    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    ax.contour(B1, B2, Z, levels=14, colors=PALETTE[0], linewidths=0.8, alpha=0.8)
    ax.plot(circle_x, circle_y, color=PALETTE[1], linewidth=2,
            label=r'L2 constraint: $\|\beta\|_2 \leq t$')
    ax.scatter(*beta_ols, marker='x', s=70, color=PALETTE[4], linewidth=2,
               label='OLS estimate (unconstrained)', zorder=5)
    ax.scatter(*beta_ridge, s=70, color=PALETTE[1], zorder=6,
               label='Ridge solution (tangency point)')
    ax.axhline(0, color='gray', linewidth=0.5)
    ax.axvline(0, color='gray', linewidth=0.5)
    ax.set_xlabel(r'$\beta_1$')
    ax.set_ylabel(r'$\beta_2$')
    ax.set_aspect('equal')
    ax.set_xlim(lim_lo, lim_hi)
    ax.set_ylim(lim_lo, lim_hi)
    ax.legend(fontsize=8, frameon=False, loc='lower left')
    fig.tight_layout()
    fig.savefig('figures/fig04_l2_geometry.png', bbox_inches='tight')
    plt.close(fig)


def fig05_l1_geometry():
    """Slide 11: elliptical loss contours + diamond L1 constraint region."""
    rng = np.random.default_rng(11)
    n = 40
    rho = 0.7
    cov = [[1.0, rho], [rho, 1.0]]
    X = rng.multivariate_normal([0, 0], cov, size=n)
    beta_true = np.array([3.0, 2.0])
    y = X @ beta_true + rng.normal(0, 1.0, size=n)

    beta_ols = np.linalg.lstsq(X, y, rcond=None)[0]
    beta_lasso = lasso_fit(X, y, lam=100.0)
    t = np.abs(beta_lasso).sum()

    b1 = np.linspace(-2, 5, 250)
    b2 = np.linspace(-2, 5, 250)
    B1, B2 = np.meshgrid(b1, b2)
    Z = np.zeros_like(B1)
    for i in range(B1.shape[0]):
        diff = y[:, None] - X[:, [0]] * B1[i, :] - X[:, [1]] * B2[i, :]
        Z[i, :] = (diff ** 2).sum(axis=0)

    diamond_x = [t, 0, -t, 0, t]
    diamond_y = [0, t, 0, -t, 0]

    lim_lo, lim_hi = -2, 5

    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    ax.contour(B1, B2, Z, levels=14, colors=PALETTE[0], linewidths=0.8, alpha=0.8)
    ax.plot(diamond_x, diamond_y, color=PALETTE[1], linewidth=2,
            label=r'L1 constraint: $\|\beta\|_1 \leq t$')
    ax.scatter(*beta_ols, marker='x', s=70, color=PALETTE[4], linewidth=2,
               label='OLS estimate (unconstrained)', zorder=5)
    ax.scatter(*beta_lasso, s=70, color=PALETTE[1], zorder=6,
               label='Lasso solution (corner tangency)')
    ax.axhline(0, color='gray', linewidth=0.5)
    ax.axvline(0, color='gray', linewidth=0.5)
    ax.set_xlabel(r'$\beta_1$')
    ax.set_ylabel(r'$\beta_2$')
    ax.set_aspect('equal')
    ax.set_xlim(lim_lo, lim_hi)
    ax.set_ylim(lim_lo, lim_hi)
    ax.legend(fontsize=8, frameon=False, loc='lower left')
    fig.tight_layout()
    fig.savefig('figures/fig05_l1_geometry.png', bbox_inches='tight')
    plt.close(fig)


def fig06_lasso_path_cv():
    """Slide 13: lasso regularization path + validation-error curve for choosing lambda."""
    rng = np.random.default_rng(5)
    n, p = 80, 5
    X = rng.normal(size=(n, p))
    X = (X - X.mean(axis=0)) / X.std(axis=0)
    beta_true = np.array([4.0, -3.0, 0.0, 0.0, 2.0])
    y = X @ beta_true + rng.normal(0, 1.5, size=n)

    idx = rng.permutation(n)
    train_idx, val_idx = idx[:50], idx[50:]
    X_train, y_train = X[train_idx], y[train_idx]
    X_val, y_val = X[val_idx], y[val_idx]

    lambdas = np.logspace(-2, 1.6, 60)
    coef_paths = np.zeros((len(lambdas), p))
    val_errors = np.zeros(len(lambdas))
    for i, lam in enumerate(lambdas):
        beta = lasso_fit(X_train, y_train, lam)
        coef_paths[i] = beta
        val_errors[i] = np.mean((y_val - X_val @ beta) ** 2)

    best_i = int(np.argmin(val_errors))
    best_lambda = lambdas[best_i]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))

    ax = axes[0]
    colors = [PALETTE[i % len(PALETTE)] for i in range(p)]
    for j in range(p):
        ax.plot(lambdas, coef_paths[:, j], color=colors[j], linewidth=1.8,
                label=f'$\\beta_{{{j+1}}}$')
    ax.axvline(best_lambda, color='gray', linestyle='--', linewidth=1)
    ax.axhline(0, color='gray', linewidth=0.6)
    ax.set_xscale('log')
    ax.set_xlabel(r'$\lambda$ (log scale)')
    ax.set_ylabel('Coefficient value')
    ax.set_title('Regularization path')
    ax.legend(fontsize=7.5, frameon=False, ncol=2, loc='upper right')

    ax2 = axes[1]
    ax2.plot(lambdas, val_errors, color=PALETTE[1], linewidth=1.8)
    ax2.scatter([best_lambda], [val_errors[best_i]], color=PALETTE[1], s=60, zorder=5,
                label=f'chosen by CV')
    ax2.axvline(best_lambda, color='gray', linestyle='--', linewidth=1)
    ax2.set_xscale('log')
    ax2.set_xlabel(r'$\lambda$ (log scale)')
    ax2.set_ylabel('Validation error (MSE)')
    ax2.set_title('Cross-validation curve')
    ax2.legend(fontsize=8.5, frameon=False)

    fig.tight_layout()
    fig.savefig('figures/fig06_lasso_path_cv.png', bbox_inches='tight')
    plt.close(fig)


# ── Run all ───────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    fig01_polynomial_fits()
    fig02_train_val_error()
    fig03_ridge_shrinkage()
    fig04_l2_geometry()
    fig05_l1_geometry()
    fig06_lasso_path_cv()
    print("Done.")
