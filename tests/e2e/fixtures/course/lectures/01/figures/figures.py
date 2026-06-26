"""Lecture 01 figures — sampling and aliasing.

Deterministic, headless (Agg backend). Run from the lecture directory:
    cd lectures/01 && python figures/figures.py
Writes fig01_sampling.png and fig02_aliasing.png next to this script.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

OUT = Path(__file__).resolve().parent


def fig01_sampling():
    t = np.linspace(0, 1, 1000)
    y = np.sin(2 * np.pi * 3 * t)
    ts = np.linspace(0, 1, 25)
    ys = np.sin(2 * np.pi * 3 * ts)
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.plot(t, y, label="continuous signal")
    ax.stem(ts, ys, linefmt="C1-", markerfmt="C1o", basefmt=" ", label="samples")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("amplitude")
    ax.set_title("Adequately sampled sine")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "fig01_sampling.png", dpi=150)
    plt.close(fig)


def fig02_aliasing():
    t = np.linspace(0, 1, 1000)
    fast = np.sin(2 * np.pi * 9 * t)
    ts = np.linspace(0, 1, 11)
    ys = np.sin(2 * np.pi * 9 * ts)
    alias = np.sin(2 * np.pi * 1 * t)
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.plot(t, fast, color="0.7", label="true 9 Hz signal")
    ax.plot(t, alias, "C3--", label="apparent 1 Hz alias")
    ax.plot(ts, ys, "ko", label="samples (11 Hz)")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("amplitude")
    ax.set_title("Undersampling produces an alias")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "fig02_aliasing.png", dpi=150)
    plt.close(fig)


def main():
    fig01_sampling()
    fig02_aliasing()
    print("wrote:", *(p.name for p in sorted(OUT.glob("*.png"))))


if __name__ == "__main__":
    main()
