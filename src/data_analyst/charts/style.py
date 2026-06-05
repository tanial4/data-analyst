"""Shared matplotlib styling for every chart.

Importing this module configures matplotlib to use the non-interactive ``Agg``
backend (required for rendering to PNG on a headless server)."""

from __future__ import annotations

import os
import tempfile
import uuid

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  (must follow backend selection)

# Muted editorial categorical palette (deep teal accent + harmonious earth tones)
# to match the paper-and-ink UI. No neon, no pastel candy.
PALETTE = [
    "#2f6b5f", "#c2823f", "#56678a", "#a8584f",
    "#7d8a6a", "#806b91", "#b59a4d", "#7a7773",
]


def setup_light_style() -> None:
    """Apply the paper-and-ink theme to matplotlib's global rcParams."""
    plt.rcParams.update(
        {
            "figure.facecolor": "#ffffff",
            "axes.facecolor": "#ffffff",
            "axes.edgecolor": "#e3e0d8",
            "axes.labelcolor": "#5f5d57",
            "axes.titlecolor": "#20201e",
            "axes.titlesize": 13,
            "axes.titleweight": "medium",
            "axes.titlepad": 14,
            "axes.grid": True,
            "grid.color": "#ebe8e1",
            "grid.linewidth": 0.8,
            "grid.alpha": 1.0,
            "xtick.color": "#8a877f",
            "ytick.color": "#8a877f",
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "text.color": "#5f5d57",
            "legend.facecolor": "#ffffff",
            "legend.edgecolor": "#e3e0d8",
            "legend.fontsize": 9,
            "font.family": "DejaVu Sans",
            "figure.dpi": 130,
        }
    )


def save_fig() -> str:
    """Save the current figure to a unique temp PNG and return its path."""
    path = os.path.join(tempfile.gettempdir(), f"chart_{uuid.uuid4().hex[:8]}.png")
    plt.tight_layout(pad=1.8)
    plt.savefig(path, dpi=130, bbox_inches="tight", facecolor="#ffffff")
    plt.close("all")
    return path
