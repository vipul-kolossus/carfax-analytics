"""
lineage.py — Metric calculation lineage diagram generator.

Renders a visual flow diagram showing source → transform → output
for the Net Revenue metric.
"""

import os
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch


# ── Color palette ──────────────────────────────────────────────────────────────
_C_SOURCE = "#1E3A5F"
_C_COL = "#1A3A2A"
_C_CALC = "#3A2A1A"
_C_OUTPUT = "#3A1A2A"
_C_BORDER_S = "#4A90D9"
_C_BORDER_C = "#5CB85C"
_C_BORDER_I = "#F0AD4E"
_C_BORDER_O = "#D9534F"
_C_TEXT = "#E8E8E8"
_C_SUBTEXT = "#A0A8B0"
_C_ARROW = "#6C8EBF"


def _box(ax, x, y, w, h, label, sublabel, bg, border, fontsize=9, subfontsize=7.5):
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.05",
        facecolor=bg, edgecolor=border, linewidth=1.5, zorder=3,
    )
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h * 0.62, label,
            ha="center", va="center", fontsize=fontsize,
            fontweight="bold", color=_C_TEXT, zorder=4)
    if sublabel:
        ax.text(x + w / 2, y + h * 0.25, sublabel,
                ha="center", va="center", fontsize=subfontsize,
                color=_C_SUBTEXT, zorder=4, style="italic")


def _arrow(ax, x1, y1, x2, y2, color=_C_ARROW, lw=1.5):
    ax.annotate(
        "",
        xy=(x2, y2), xycoords="data",
        xytext=(x1, y1), textcoords="data",
        arrowprops=dict(arrowstyle="->", color=color, lw=lw,
                        connectionstyle="arc3,rad=0.0"),
        zorder=5,
    )


def render_net_revenue_lineage(output_path: Optional[str] = None) -> str:
    """
    Render the Net Revenue metric calculation lineage diagram as a PNG.

    The diagram shows five layers:
        Layer 1 — Source tables (dlr_fin, dlr_dim)
        Layer 2 — Raw columns (inv_amt, dsc_amt, refund_amt, dealer_id, trt_cd)
        Layer 3 — JOIN and SUM aggregations
        Layer 4 — Net Revenue formula application
        Layer 5 — Output metric (Net Revenue by Territory)

    Args:
        output_path: Path to write the PNG. Defaults to 'net_revenue_lineage.png'
                     in the current working directory.

    Returns:
        str: Absolute path to the saved PNG file.

    Example:
        >>> path = render_net_revenue_lineage()
        >>> path = render_net_revenue_lineage('/tmp/lineage.png')
    """
    if output_path is None:
        output_path = os.path.join(os.getcwd(), "net_revenue_lineage.png")

    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis("off")
    fig.patch.set_facecolor("#0F1117")
    ax.set_facecolor("#0F1117")

    # Title
    ax.text(8, 9.55, "Net Revenue — Metric Calculation Lineage",
            ha="center", va="center", fontsize=14, fontweight="bold",
            color="#FFFFFF", zorder=4)
    ax.text(8, 9.2,
            "Formula:  Net Revenue = SUM(inv_amt) − SUM(dsc_amt) − SUM(refund_amt)"
            "  |  Grain: Territory (trt_cd)",
            ha="center", va="center", fontsize=8.5, color=_C_SUBTEXT, zorder=4)

    # Layer 1 — Source Tables
    ax.text(0.3, 8.55, "LAYER 1 — SOURCE TABLES", fontsize=7.5,
            color=_C_BORDER_S, fontweight="bold", va="center")
    _box(ax, 0.4, 6.8, 3.2, 1.4, "dlr_fin", "Financial Fact Table",
         _C_SOURCE, _C_BORDER_S, 10, 8)
    _box(ax, 4.0, 6.8, 3.2, 1.4, "dlr_dim", "Dealer Dimension Table",
         _C_SOURCE, _C_BORDER_S, 10, 8)

    # Layer 2 — Raw Columns
    ax.text(0.3, 6.55, "LAYER 2 — RAW COLUMNS", fontsize=7.5,
            color=_C_BORDER_C, fontweight="bold", va="center")
    col_specs = [
        (0.3, 4.9, "inv_amt", "Invoice Amount\n(dlr_fin)"),
        (2.0, 4.9, "dsc_amt", "Discount Amount\n(dlr_fin)"),
        (3.7, 4.9, "refund_amt", "Refund Amount\n(dlr_fin)"),
        (5.6, 4.9, "dealer_id", "Join Key\n(dlr_fin)"),
        (7.5, 4.9, "dealer_id", "Join Key\n(dlr_dim)"),
        (9.4, 4.9, "trt_cd", "Territory Code\n(dlr_dim)"),
    ]
    for cx, cy, lbl, sub in col_specs:
        _box(ax, cx, cy, 1.6, 1.3, lbl, sub, _C_COL, _C_BORDER_C, 8.5, 7)
    for cx in [1.1, 2.8, 4.5, 6.4]:
        _arrow(ax, 2.0, 6.8, cx, 6.2)
    for cx in [8.3, 10.2]:
        _arrow(ax, 5.6, 6.8, cx, 6.2)

    # Layer 3 — JOIN & Aggregation
    ax.text(0.3, 4.65, "LAYER 3 — JOIN & AGGREGATION", fontsize=7.5,
            color=_C_BORDER_I, fontweight="bold", va="center")
    _box(ax, 6.5, 3.3, 2.2, 1.1, "JOIN",
         "dlr_fin.dealer_id\n= dlr_dim.dealer_id",
         _C_CALC, _C_BORDER_I, 9, 7)
    _arrow(ax, 6.4, 5.55, 6.9, 4.4)
    _arrow(ax, 8.3, 5.55, 8.3, 4.4)
    sum_specs = [
        (0.3, 3.3, "SUM(inv_amt)", "Gross Invoice\nper Territory"),
        (2.15, 3.3, "SUM(dsc_amt)", "Total Discounts\nper Territory"),
        (4.0, 3.3, "SUM(refund_amt)", "Total Refunds\nper Territory"),
    ]
    for sx, sy, lbl, sub in sum_specs:
        _box(ax, sx, sy, 1.75, 1.1, lbl, sub, _C_CALC, _C_BORDER_I, 8, 7)
    _arrow(ax, 1.1, 4.9, 1.2, 4.4)
    _arrow(ax, 2.8, 4.9, 3.05, 4.4)
    _arrow(ax, 4.5, 4.9, 4.9, 4.4)
    _box(ax, 9.5, 3.3, 1.8, 1.1, "GROUP BY", "trt_cd\n(Territory)",
         _C_CALC, _C_BORDER_I, 8.5, 7)
    _arrow(ax, 10.2, 4.9, 10.4, 4.4)

    # Layer 4 — Formula
    ax.text(0.3, 3.1, "LAYER 4 — FORMULA APPLICATION", fontsize=7.5,
            color="#A060C0", fontweight="bold", va="center")
    _box(ax, 2.5, 1.7, 5.0, 1.2, "Net Revenue Formula",
         "SUM(inv_amt)  −  SUM(dsc_amt)  −  SUM(refund_amt)",
         "#2A1A3A", "#A060C0", 10, 8.5)
    for sx in [1.2, 3.05, 4.9]:
        _arrow(ax, sx + 0.875, 3.3, 5.0, 2.9, color="#A060C0")
    _arrow(ax, 10.4, 3.3, 7.5, 2.9, color="#A060C0")

    # Layer 5 — Output
    ax.text(0.3, 1.55, "LAYER 5 — OUTPUT METRIC", fontsize=7.5,
            color=_C_BORDER_O, fontweight="bold", va="center")
    _box(ax, 3.8, 0.25, 6.4, 1.1, "Net Revenue by Territory",
         "territory_code  |  dealer_count  |  net_revenue_amt",
         "#2A0A0A", _C_BORDER_O, 11, 8.5)
    _arrow(ax, 5.0, 1.7, 7.0, 1.35, color=_C_BORDER_O, lw=2.0)

    # Legend
    legend_items = [
        (mpatches.Patch(facecolor=_C_SOURCE, edgecolor=_C_BORDER_S), "Source Table"),
        (mpatches.Patch(facecolor=_C_COL, edgecolor=_C_BORDER_C), "Raw Column"),
        (mpatches.Patch(facecolor=_C_CALC, edgecolor=_C_BORDER_I), "Transform / Aggregation"),
        (mpatches.Patch(facecolor="#2A1A3A", edgecolor="#A060C0"), "Formula"),
        (mpatches.Patch(facecolor="#2A0A0A", edgecolor=_C_BORDER_O), "Output Metric"),
    ]
    ax.legend(
        handles=[h for h, _ in legend_items],
        labels=[l for _, l in legend_items],
        loc="lower right", bbox_to_anchor=(0.99, 0.01),
        fontsize=7.5, framealpha=0.3,
        facecolor="#1A1D26", edgecolor="#444", labelcolor=_C_TEXT,
    )

    plt.tight_layout(pad=0.3)
    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    return os.path.abspath(output_path)
