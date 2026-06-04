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

PALETTE = [
    "#10a37f", "#2563eb", "#f59e0b", "#ef4444",
    "#8b5cf6", "#06b6d4", "#ec4899", "#84cc16",
    "#f97316", "#0ea5e9",
]


def setup_light_style() -> None:
    """Apply the light ChatGPT-style theme to matplotlib's global rcParams."""
    plt.rcParams.update(
        {
            "figure.facecolor": "#ffffff",
            "axes.facecolor": "#f9fafb",
            "axes.edgecolor": "#e5e7eb",
            "axes.labelcolor": "#374151",
            "axes.titlecolor": "#111827",
            "axes.titlesize": 13,
            "axes.titleweight": "semibold",
            "axes.titlepad": 14,
            "axes.grid": True,
            "grid.color": "#e5e7eb",
            "grid.linewidth": 0.7,
            "grid.alpha": 1.0,
            "xtick.color": "#6b7280",
            "ytick.color": "#6b7280",
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "text.color": "#374151",
            "legend.facecolor": "#ffffff",
            "legend.edgecolor": "#e5e7eb",
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
