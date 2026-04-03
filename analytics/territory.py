"""
territory.py — Territory-level analytics functions.

Wraps net revenue queries with business-friendly aggregation,
ranking, and summary logic.
"""

from decimal import Decimal
from typing import List, Dict, Any, Optional
from ..queries.net_revenue import get_net_revenue_by_territory


def get_territory_summary() -> Dict[str, Any]:
    """
    Return a high-level summary of net revenue across all territories.

    Computes: total net revenue, total dealers, top territory, bottom territory,
    average revenue per territory, and average revenue per dealer.

    Returns:
        Dict with keys:
            territory_count (int): Number of territories.
            total_net_revenue (Decimal): Sum of net revenue across all territories.
            total_dealers (int): Total distinct dealers.
            top_territory (str): Territory with highest net revenue.
            top_territory_revenue (Decimal): Revenue for the top territory.
            bottom_territory (str): Territory with lowest net revenue.
            bottom_territory_revenue (Decimal): Revenue for the bottom territory.
            avg_revenue_per_territory (float): Mean net revenue per territory.
            avg_revenue_per_dealer (float): Mean net revenue per dealer.

    Example:
        >>> summary = get_territory_summary()
        >>> print(summary['top_territory'], summary['top_territory_revenue'])
    """
    rows = get_net_revenue_by_territory()
    if not rows:
        return {}

    total_revenue = sum(r["net_revenue"] or Decimal(0) for r in rows)
    total_dealers = sum(r["dealer_count"] or 0 for r in rows)
    sorted_rows = sorted(rows, key=lambda r: r["net_revenue"] or Decimal(0), reverse=True)

    return {
        "territory_count": len(rows),
        "total_net_revenue": total_revenue,
        "total_dealers": total_dealers,
        "top_territory": sorted_rows[0]["territory_code"],
        "top_territory_revenue": sorted_rows[0]["net_revenue"],
        "bottom_territory": sorted_rows[-1]["territory_code"],
        "bottom_territory_revenue": sorted_rows[-1]["net_revenue"],
        "avg_revenue_per_territory": float(total_revenue) / len(rows) if rows else 0,
        "avg_revenue_per_dealer": float(total_revenue) / total_dealers if total_dealers else 0,
    }


def get_top_territories(n: int = 5) -> List[Dict[str, Any]]:
    """
    Return the top N territories by net revenue.

    Args:
        n: Number of top territories to return (default: 5).

    Returns:
        List of up to n territory dicts, sorted by net_revenue descending.
        Each dict contains: territory_code, dealer_count, total_invoice_amt,
        total_discount_amt, total_refund_amt, net_revenue.

    Example:
        >>> top5 = get_top_territories(5)
        >>> for t in top5:
        ...     print(t['territory_code'], t['net_revenue'])
    """
    rows = get_net_revenue_by_territory()
    sorted_rows = sorted(rows, key=lambda r: r["net_revenue"] or Decimal(0), reverse=True)
    return sorted_rows[:n]


def get_territory_ranking(
    territories: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Return territories with their rank by net revenue.

    Args:
        territories: Optional list of territory codes to include.
                     If None, ranks all territories.

    Returns:
        List of dicts with all net revenue fields plus a 'rank' key (1 = highest revenue).

    Example:
        >>> ranked = get_territory_ranking()
        >>> ranked = get_territory_ranking(territories=['EAST', 'WEST', 'NORTH'])
    """
    rows = get_net_revenue_by_territory(territories=territories)
    sorted_rows = sorted(rows, key=lambda r: r["net_revenue"] or Decimal(0), reverse=True)
    for i, row in enumerate(sorted_rows, start=1):
        row["rank"] = i
    return sorted_rows
