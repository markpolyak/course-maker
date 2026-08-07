"""
Lecture 2 figures — Regularization in Practice & Deep Learning
Generates: fig01_elastic_net_grouping.png, fig02_early_stopping.png,
           fig04_data_augmentation.png
(fig03 / V03, the dropout diagram, is TikZ and lives directly in slides.tex.)
Run from the lecture directory: python figures/figures.py

Dependency note: fig04 uses scikit-image (skimage.data.cat()) for a real
sample photo instead of a hand-drawn synthetic image. skimage.data.cat() is
bundled directly in the scikit-image package (no network access needed at
runtime). Install with: pip install scikit-image
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from skimage import data, transform, img_as_float

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


def elastic_net_fit(X, y, lam1, lam2, n_iter=500, tol=1e-9):
    """Coordinate descent for: minimize 0.5*||y - Xb||^2 + lam1*||b||_1 + 0.5*lam2*||b||_2^2."""
    n, p = X.shape
    beta = np.zeros(p)
    col_sq = (X ** 2).sum(axis=0)
    for _ in range(n_iter):
        beta_old = beta.copy()
        for j in range(p):
            denom = col_sq[j] + lam2
            if denom == 0:
                beta[j] = 0.0
                continue
            residual = y - X @ beta + X[:, j] * beta[j]
            rho = X[:, j] @ residual
            beta[j] = soft_threshold(rho, lam1) / denom
        if np.max(np.abs(beta - beta_old)) < tol:
            break
    return beta


def lasso_fit(X, y, lam, n_iter=500, tol=1e-9):
    """Special case of elastic net with lam2 = 0."""
    return elastic_net_fit(X, y, lam1=lam, lam2=0.0, n_iter=n_iter, tol=tol)


# ── Figure functions ───────────────────────────────────────────────────────────

def fig01_elastic_net_grouping():
    """Slide 5: coefficients of two correlated features under ridge / lasso / elastic net."""
    rng = np.random.default_rng(11)
    n = 40
    rho = 0.7
    cov = [[1.0, rho], [rho, 1.0]]
    X = rng.multivariate_normal([0, 0], cov, size=n)
    beta_true = np.array([3.0, 2.0])
    y = X @ beta_true + rng.normal(0, 1.0, size=n)

    beta_ridge = ridge_fit(X, y, lam=8.0)
    beta_lasso = lasso_fit(X, y, lam=100.0)
    beta_enet = elastic_net_fit(X, y, lam1=40.0, lam2=40.0)

    methods = ['Ridge', 'Lasso', 'Elastic Net']
    coefs = np.array([beta_ridge, beta_lasso, beta_enet])

    fig, ax = plt.subplots(figsize=(6.5, 4))
    x = np.arange(len(methods))
    width = 0.32
    ax.bar(x - width / 2, coefs[:, 0], width, color=PALETTE[0], label=r'$\beta_1$')
    ax.bar(x + width / 2, coefs[:, 1], width, color=PALETTE[1], label=r'$\beta_2$')
    ax.axhline(0, color='gray', linewidth=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(methods)
    ax.set_ylabel('Fitted coefficient value')
    ax.legend(fontsize=9, frameon=False)
    fig.tight_layout()
    fig.savefig('figures/fig01_elastic_net_grouping.png', bbox_inches='tight')
    plt.close(fig)


def fig02_early_stopping():
    """Slide 8: training loss vs. validation loss over epochs, with early-stopping point."""
    rng = np.random.default_rng(21)
    epochs = np.arange(1, 61)

    train_loss = 0.15 + 1.6 * np.exp(-epochs / 12.0) + rng.normal(0, 0.01, size=epochs.shape)
    train_loss = np.clip(train_loss, 0.02, None)

    val_base = 0.35 + 1.6 * np.exp(-epochs / 12.0)
    overfit_term = 0.00035 * np.clip(epochs - 18, 0, None) ** 1.6
    val_loss = val_base + overfit_term + rng.normal(0, 0.012, size=epochs.shape)

    best_epoch = epochs[int(np.argmin(val_loss))]

    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(epochs, train_loss, color=PALETTE[0], linewidth=1.8, label='Training loss')
    ax.plot(epochs, val_loss, color=PALETTE[1], linewidth=1.8, label='Validation loss')
    ax.axvline(best_epoch, color=PALETTE[4], linestyle='--', linewidth=1.2)
    ax.scatter([best_epoch], [val_loss[int(np.argmin(val_loss))]], color=PALETTE[1],
               s=55, zorder=5, label='Early-stopping point')
    ax.text(best_epoch + 1, ax.get_ylim()[1] * 0.92, 'stop here', color=PALETTE[4], fontsize=8.5)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss')
    ax.legend(fontsize=9, frameon=False)
    fig.tight_layout()
    fig.savefig('figures/fig02_early_stopping.png', bbox_inches='tight')
    plt.close(fig)


def fig04_data_augmentation():
    """Slide 13: one real photo + several label-preserving augmentations."""
    base = img_as_float(data.cat())  # (300, 451, 3), bundled sample photo, no network needed

    rotated = transform.rotate(base, angle=12, mode='edge')
    flipped = np.fliplr(base)
    shifted = np.roll(base, shift=(20, -30), axis=(0, 1))
    brightened = np.clip(base * 0.7 + 0.25, 0, 1)

    images = [base, rotated, flipped, shifted, brightened]
    titles = ['Original', 'Rotated', 'Flipped', 'Shifted', 'Brightness-jittered']

    fig, axes = plt.subplots(1, 5, figsize=(12, 2.8))
    for ax, img, title in zip(axes, images, titles):
        ax.imshow(img)
        ax.set_title(title, fontsize=9.5)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color('#cccccc')
    fig.suptitle('Same label throughout: "cat"', y=1.02, fontsize=10)
    fig.tight_layout()
    fig.savefig('figures/fig04_data_augmentation.png', bbox_inches='tight')
    plt.close(fig)


# ── Run all ───────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    fig01_elastic_net_grouping()
    fig02_early_stopping()
    fig04_data_augmentation()
    print("Done.")
