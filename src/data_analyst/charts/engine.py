"""Matplotlib chart factory.

``make_chart`` dispatches on ``chart_type`` to a renderer. Every renderer is
defensive: it returns ``None`` (rather than raising) when the requested columns
are missing or contain no plottable data, so a failed chart never aborts a
turn.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

from ..core.helpers import pick_num
from .style import PALETTE, save_fig, setup_light_style
from .style import plt  # re-exported, Agg backend already selected


def make_chart(
    chart_type: str,
    data: pd.DataFrame,
    x: str | None,
    y: str | None,
    title: str,
) -> str | None:
    """Render ``chart_type`` from ``data`` and return a PNG path, or ``None``."""
    if chart_type == "none" or data is None or data.empty:
        return None

    renderer = _RENDERERS.get(chart_type)
    if renderer is None:
        return None

    setup_light_style()
    try:
        return renderer(data, x, y, title)
    except Exception as e:  # never let a chart failure break the turn
        print(f"[chart error] {e}")
        plt.close("all")
        return None


def _bar(data, x, y, title):
    if x not in data.columns or y not in data.columns:
        return None
    df2 = data[[x, y]].copy()
    df2[y] = pd.to_numeric(df2[y], errors="coerce")
    df2 = df2.dropna(subset=[y]).head(25)
    if df2.empty:
        return None
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(df2))]
    bars = ax.bar(df2[x].astype(str), df2[y], color=colors, edgecolor="white", linewidth=0.6, width=0.62)
    ax.bar_label(bars, fmt="%.4g", padding=3, color="#8a877f", fontsize=8)
    ax.set_xlabel(x, labelpad=8, color="#8a877f", fontsize=10)
    ax.set_ylabel(y, labelpad=8, color="#8a877f", fontsize=10)
    ax.set_title(title, color="#20201e", fontsize=13, fontweight="semibold")
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#e3e0d8")
    plt.xticks(rotation=35, ha="right")
    return save_fig()


def _line(data, x, y, title):
    if x not in data.columns or y not in data.columns:
        return None
    df2 = data[[x, y]].copy()
    df2[y] = pd.to_numeric(df2[y], errors="coerce")
    df2 = df2.dropna(subset=[y]).head(200)
    if df2.empty:
        return None
    fig, ax = plt.subplots(figsize=(10, 5))
    xs = range(len(df2))
    ax.plot(xs, df2[y], color=PALETTE[0], linewidth=2.2, marker="o", markersize=3.5,
            markerfacecolor="white", markeredgecolor=PALETTE[0], markeredgewidth=1.5)
    ax.fill_between(xs, df2[y], alpha=0.07, color=PALETTE[0])
    ax.set_xlabel(x, labelpad=8, color="#8a877f", fontsize=10)
    ax.set_ylabel(y, labelpad=8, color="#8a877f", fontsize=10)
    ax.set_title(title, color="#20201e", fontsize=13, fontweight="semibold")
    step = max(1, len(df2) // 10)
    ax.set_xticks(range(0, len(df2), step))
    ax.set_xticklabels(df2[x].astype(str).iloc[::step], rotation=35, ha="right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#e3e0d8")
    return save_fig()


def _area(data, x, y, title):
    if x not in data.columns or y not in data.columns:
        return None
    df2 = data[[x, y]].copy()
    df2[y] = pd.to_numeric(df2[y], errors="coerce")
    df2 = df2.dropna(subset=[y]).head(200)
    if df2.empty:
        return None
    fig, ax = plt.subplots(figsize=(10, 5))
    xs = range(len(df2))
    ax.fill_between(xs, df2[y], alpha=0.18, color=PALETTE[0])
    ax.plot(xs, df2[y], color=PALETTE[0], linewidth=2)
    ax.set_xlabel(x, labelpad=8, color="#8a877f", fontsize=10)
    ax.set_ylabel(y, labelpad=8, color="#8a877f", fontsize=10)
    ax.set_title(title, color="#20201e", fontsize=13, fontweight="semibold")
    step = max(1, len(df2) // 10)
    ax.set_xticks(range(0, len(df2), step))
    ax.set_xticklabels(df2[x].astype(str).iloc[::step], rotation=35, ha="right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#e3e0d8")
    return save_fig()


def _pie(data, x, y, title, donut=False):
    if x not in data.columns or y not in data.columns:
        return None
    df2 = data[[x, y]].copy()
    df2[y] = pd.to_numeric(df2[y], errors="coerce").fillna(0)
    df2 = df2.groupby(x, dropna=False)[y].sum().reset_index().head(10)
    if df2.empty:
        return None
    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        df2[y], labels=df2[x].astype(str), autopct="%1.1f%%", colors=PALETTE[: len(df2)],
        wedgeprops={"linewidth": 2, "edgecolor": "white"}, pctdistance=0.78, startangle=90,
    )
    for t in texts:
        t.set_color("#5f5d57")
        t.set_fontsize(9)
    for t in autotexts:
        t.set_color("white")
        t.set_fontsize(8)
        t.set_fontweight("bold")
    if donut:
        ax.add_patch(plt.Circle((0, 0), 0.55, fc="white"))
    ax.set_title(title, color="#20201e", fontsize=13, fontweight="semibold", pad=16)
    return save_fig()


def _histogram(data, x, y, title):
    col = x if (x and x in data.columns) else pick_num(data)
    if col is None:
        return None
    series = pd.to_numeric(data[col], errors="coerce").dropna()
    if series.empty:
        return None
    fig, ax = plt.subplots(figsize=(10, 5))
    n, bins, patches = ax.hist(series, bins=30, color=PALETTE[0], edgecolor="white", linewidth=0.5, alpha=0.85)
    for i, patch in enumerate(patches):
        patch.set_facecolor(PALETTE[i % 3])
    ax.axvline(series.mean(), color=PALETTE[3], linewidth=1.6, linestyle="--", label=f"Mean: {series.mean():.4g}")
    ax.axvline(series.median(), color=PALETTE[1], linewidth=1.6, linestyle="--", label=f"Median: {series.median():.4g}")
    ax.legend(framealpha=0.9)
    ax.set_xlabel(col, labelpad=8, color="#8a877f", fontsize=10)
    ax.set_ylabel("Frequency", labelpad=8, color="#8a877f", fontsize=10)
    ax.set_title(title, color="#20201e", fontsize=13, fontweight="semibold")
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#e3e0d8")
    return save_fig()


def _scatter(data, x, y, title):
    if x not in data.columns or y not in data.columns:
        return None
    df2 = data[[x, y]].copy()
    df2[x] = pd.to_numeric(df2[x], errors="coerce")
    df2[y] = pd.to_numeric(df2[y], errors="coerce")
    df2 = df2.dropna().head(800)
    if df2.empty:
        return None
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(df2[x], df2[y], color=PALETTE[0], alpha=0.55, s=22, edgecolors="none")
    m, b = np.polyfit(df2[x], df2[y], 1)
    xr = np.linspace(df2[x].min(), df2[x].max(), 200)
    ax.plot(xr, m * xr + b, color=PALETTE[3], linewidth=1.8, linestyle="--", label="Linear trend")
    corr = df2[x].corr(df2[y])
    ax.set_title(f"{title}  (r = {corr:.3f})", color="#20201e", fontsize=13, fontweight="semibold")
    ax.set_xlabel(x, labelpad=8, color="#8a877f", fontsize=10)
    ax.set_ylabel(y, labelpad=8, color="#8a877f", fontsize=10)
    ax.legend(framealpha=0.9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#e3e0d8")
    return save_fig()


def _box(data, x, y, title):
    col = y if (y and y in data.columns) else (x if (x and x in data.columns) else pick_num(data))
    if col is None:
        return None
    series = pd.to_numeric(data[col], errors="coerce").dropna()
    if series.empty:
        return None
    fig, ax = plt.subplots(figsize=(5, 7))
    ax.boxplot(
        series, patch_artist=True,
        medianprops=dict(color=PALETTE[3], linewidth=2),
        boxprops=dict(facecolor="#e0f2fe", alpha=0.8),
        whiskerprops=dict(color=PALETTE[0]),
        capprops=dict(color=PALETTE[0]),
        flierprops=dict(marker="o", color=PALETTE[3], alpha=0.45, markersize=4),
    )
    stats = series.describe()
    ax.text(
        0.5, -0.06,
        f"Mean: {stats['mean']:.4g}   Median: {stats['50%']:.4g}\n"
        f"Min: {stats['min']:.4g}   Max: {stats['max']:.4g}   Std: {stats['std']:.4g}",
        transform=ax.transAxes, ha="center", va="top", fontsize=8.5, color="#8a877f",
    )
    ax.set_title(title, color="#20201e", fontsize=13, fontweight="semibold")
    ax.set_ylabel(col, labelpad=8, color="#8a877f", fontsize=10)
    ax.set_xticks([])
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#e3e0d8")
    return save_fig()


def _heatmap(data, x, y, title):
    num_cols = data.select_dtypes(include="number").columns.tolist()
    if len(num_cols) < 2:
        return None
    corr = data[num_cols].corr()
    n = len(num_cols)
    fig, ax = plt.subplots(figsize=(max(7, n), max(5, n - 1)))
    # Diverging colormap: teal (negative) -> paper (zero) -> clay (positive).
    corr_cmap = LinearSegmentedColormap.from_list(
        "corr_div", ["#2f6b5f", "#f4f3ef", "#a8584f"]
    )
    im = ax.imshow(corr.values, cmap=corr_cmap, vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(num_cols, rotation=45, ha="right", fontsize=8.5)
    ax.set_yticklabels(num_cols, fontsize=8.5)
    for i in range(n):
        for j in range(n):
            val = corr.values[i, j]
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=7.5,
                    color="#20201e")
    plt.colorbar(im, ax=ax, shrink=0.8)
    ax.set_title(title, color="#20201e", fontsize=13, fontweight="bold")
    return save_fig()


_RENDERERS = {
    "bar": _bar,
    "line": _line,
    "area": _area,
    "pie": _pie,
    "donut": lambda data, x, y, title: _pie(data, x, y, title, donut=True),
    "histogram": _histogram,
    "scatter": _scatter,
    "box": _box,
    "heatmap": _heatmap,
}
