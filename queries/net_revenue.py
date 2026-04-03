"""
net_revenue.py — Net Revenue by Territory query.

Business metric: Net Revenue = SUM(inv_amt) - SUM(dsc_amt) - SUM(refund_amt)
Grain: One row per territory (trt_cd)
Source tables: carfax_operations.dlr_fin (fact), carfax_operations.dlr_dim (dimension)
"""

from typing import List, Dict, Any, Optional
from ..connections import get_postgres_connection


_SQL_NET_REVENUE_BY_TERRITORY = """
SELECT
    -- Territory grouping from dealer dimension
    d.trt_cd                                        AS territory_code,

    -- Dealer count at territory grain
    COUNT(DISTINCT d.dealer_id)                     AS dealer_count,

    -- Gross invoiced amount before deductions
    SUM(f.inv_amt)                                  AS total_invoice_amt,

    -- Total discounts applied
    SUM(f.dsc_amt)                                  AS total_discount_amt,

    -- Total refunds issued
    SUM(f.refund_amt)                               AS total_refund_amt,

    -- Net Revenue formula: Invoice - Discounts - Refunds
    SUM(f.inv_amt - f.dsc_amt - f.refund_amt)       AS net_revenue

FROM
    -- Fact table: one row per dealer financial transaction
    carfax_operations.dlr_fin  f

    -- Dimension table: dealer attributes including territory
    INNER JOIN carfax_operations.dlr_dim  d
        ON d.dealer_id = f.dealer_id   -- MANY-TO-ONE join (fact → dim)

GROUP BY
    d.trt_cd

ORDER BY
    net_revenue DESC
"""

_SQL_NET_REVENUE_FILTERED = """
SELECT
    d.trt_cd                                        AS territory_code,
    COUNT(DISTINCT d.dealer_id)                     AS dealer_count,
    SUM(f.inv_amt)                                  AS total_invoice_amt,
    SUM(f.dsc_amt)                                  AS total_discount_amt,
    SUM(f.refund_amt)                               AS total_refund_amt,
    SUM(f.inv_amt - f.dsc_amt - f.refund_amt)       AS net_revenue
FROM
    carfax_operations.dlr_fin  f
    INNER JOIN carfax_operations.dlr_dim  d
        ON d.dealer_id = f.dealer_id
WHERE
    d.trt_cd = ANY(%(territories)s)
GROUP BY
    d.trt_cd
ORDER BY
    net_revenue DESC
"""


def get_net_revenue_by_territory(
    territories: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Return net revenue aggregated by territory.

    Net Revenue formula (per Business Glossary):
        SUM(inv_amt) - SUM(dsc_amt) - SUM(refund_amt)

    Args:
        territories: Optional list of territory codes to filter by (e.g., ['T1', 'T2']).
                     If None, returns all territories.

    Returns:
        List of dicts with keys:
            territory_code (str): Territory identifier (trt_cd).
            dealer_count (int): Number of distinct dealers in the territory.
            total_invoice_amt (Decimal): Sum of gross invoice amounts.
            total_discount_amt (Decimal): Sum of discounts applied.
            total_refund_amt (Decimal): Sum of refunds issued.
            net_revenue (Decimal): Net revenue after discounts and refunds.

    Raises:
        psycopg2.DatabaseError: On query execution failure.
        ValueError: If environment credentials are missing.

    Example:
        >>> rows = get_net_revenue_by_territory()
        >>> for row in rows:
        ...     print(row['territory_code'], row['net_revenue'])

        >>> rows = get_net_revenue_by_territory(territories=['EAST', 'WEST'])
    """
    conn = get_postgres_connection()
    try:
        with conn.cursor() as cur:
            if territories:
                cur.execute(_SQL_NET_REVENUE_FILTERED, {"territories": territories})
            else:
                cur.execute(_SQL_NET_REVENUE_BY_TERRITORY)
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()
