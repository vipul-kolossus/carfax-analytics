"""
charts.py — Matplotlib chart helpers for Carfax analytics output.
"""

import os
from typing import List, Dict, Any, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def bar_chart_territory_revenue(
    rows: List[Dict[str, Any]],
    output_path: Optional[str] = None,
    title: str = "Net Revenue by Territory",
    top_n: int = 20,
) -> str:
    """
    Render a horizontal bar chart of net revenue by territory.

    Args:
        rows: List of dicts from get_net_revenue_by_territory().
              Must contain 'territory_code' and 'net_revenue' keys.
        output_path: Path to save PNG. Defaults to 'territory_revenue.png'
                     in the current directory.
        title: Chart title string.
        top_n: Maximum number of territories to display (default: 20).

    Returns:
        str: Absolute path to saved PNG file.

    Example:
        >>> from carfax_analytics.queries import get_net_revenue_by_territory
        >>> from carfax_analytics.visualizations import bar_chart_territory_revenue
        >>> rows = get_net_revenue_by_territory()
        >>> path = bar_chart_territory_revenue(rows)
    """
    if output_path is None:
        output_path = os.path.join(os.getcwd(), "territory_revenue.png")

    sorted_rows = sorted(
        rows,
        key=lambda r: float(r.get("net_revenue") or 0),
        reverse=False,
    )[-top_n:]

    labels = [r["territory_code"] for r in sorted_rows]
    values = [float(r.get("net_revenue") or 0) for r in sorted_rows]

    fig, ax = plt.subplots(figsize=(12, max(6, len(labels) * 0.45)))
    fig.patch.set_facecolor("#0F1117")
    ax.set_facecolor("#0F1117")

    bars = ax.barh(labels, values, color="#4A90D9", edgecolor="#2A5080", linewidth=0.8)

    # Annotate bar values
    for bar, val in zip(bars, values):
        ax.text(
            val * 1.005,
            bar.get_y() + bar.get_height() / 2,
            f"${val:,.0f}",
            va="center",
            fontsize=8,
            color="#E8E8E8",
        )

    ax.set_xlabel("Net Revenue (USD)", color="#A0A8B0", fontsize=10)
    ax.set_title(title, color="#FFFFFF", fontsize=13, fontweight="bold", pad=12)
    ax.tick_params(colors="#A0A8B0")
    ax.spines["bottom"].set_color("#333")
    ax.spines["left"].set_color("#333")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.label.set_color("#A0A8B0")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    return os.path.abspath(output_path)
