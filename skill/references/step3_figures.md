# Step 3 — Python Figure Script

## Context to gather before writing

From `lectures/NN/visuals.md`:
- All rows where TikZ = "No" or "Hard"
- Figure ID, slide number, description

From `history.md`:
- Any figures the user rejected with visual feedback
  ("too busy", "wrong color", "axis labels unclear", etc.)

## Script structure: `lectures/NN/figures/figures.py`

```python
"""
Lecture N figures
Generates: fig01_name.png, fig02_name.png, ...
Run from the lecture directory: python figures/figures.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy import signal  # only if needed
import statsmodels.api as sm  # only if needed

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

# ── Figure functions ───────────────────────────────────────────────────────────

def fig01_name():
    """Slide 4: ACF for AR(2) process"""
    fig, ax = plt.subplots(figsize=(6, 3))
    # ... plotting code ...
    fig.savefig('figures/fig01_name.png', bbox_inches='tight')
    plt.close(fig)

def fig02_name():
    """Slide 9: stationary vs non-stationary"""
    # ...

# ── Run all ───────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    fig01_name()
    fig02_name()
    print("Done.")
```

## File naming convention

`figNN_snake_case_description.png`

- NN = two-digit figure number matching visuals.md (V01 → fig01)
- snake_case: 2–4 words describing the figure content
- Examples: `fig01_acf_ar2.png`, `fig03_stationary_vs_nonstationary.png`

## Style rules

- `dpi=180`, `bbox_inches='tight'`, white background
- Axis labels in the language specified in `CLAUDE.md` → Course context
- Spines: remove top and right
- No grid by default; add light grid only for plots where reading values matters
- Color palette: use `PALETTE` list above (dark blue, red, orange, light blue, green)
- One figure per function; each function saves and closes its figure
- Minimum dependencies: `numpy`, `matplotlib`, `scipy`, `statsmodels`
  Do not add other packages without noting it to the user

## Execution and verification

After saving `figures.py`, always run it:
```bash
cd lectures/NN && python figures/figures.py
```

The script is considered unverified until it has been run at least once without errors.
**Never mark the figures step ✅ without a successful run.**

If the run fails:
- Show the full traceback to the user
- Fix the offending function only (don't rewrite the whole script)
- Re-run until clean

After a clean run, list the generated PNG files so the user can confirm the output looks right.

## Iteration handling

When the user gives visual feedback ("make the font larger", "remove the legend",
"the x-axis label overlaps"), update only the affected function, re-run the script,
confirm the PNG was regenerated.
Append to history.md what was changed and why.

## Common mistakes to avoid

- Forgetting `plt.close(fig)` — causes memory leak in long scripts
- Using `plt.show()` — blocks execution, use `fig.savefig()` instead
- Hardcoding absolute paths — paths relative to script location only
- Not fixing the random seed — makes figures non-reproducible
- Creating figures with tight layouts that clip labels
