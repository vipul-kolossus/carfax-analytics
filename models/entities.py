"""
entities.py — Typed data models for Carfax analytics results.

Uses dataclasses for lightweight, dependency-free entity definitions.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


@dataclass
class TerritoryRevenue:
    """
    Represents net revenue aggregated at the territory grain.

    Attributes:
        territory_code: Territory identifier (trt_cd).
        dealer_count: Number of distinct dealers in this territory.
        total_invoice_amt: Gross invoiced amount before deductions.
        total_discount_amt: Total discounts applied.
        total_refund_amt: Total refunds issued.
        net_revenue: Net Revenue = inv_amt - dsc_amt - refund_amt.
        rank: Optional rank by net revenue (1 = highest).
    """

    territory_code: str
    dealer_count: int
    total_invoice_amt: Decimal
    total_discount_amt: Decimal
    total_refund_amt: Decimal
    net_revenue: Decimal
    rank: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> "TerritoryRevenue":
        """
        Construct a TerritoryRevenue from a raw query result dict.

        Args:
            data: Dict returned by get_net_revenue_by_territory().

        Returns:
            TerritoryRevenue instance.
        """
        return cls(
            territory_code=data["territory_code"],
            dealer_count=int(data["dealer_count"]),
            total_invoice_amt=Decimal(str(data.get("total_invoice_amt") or 0)),
            total_discount_amt=Decimal(str(data.get("total_discount_amt") or 0)),
            total_refund_amt=Decimal(str(data.get("total_refund_amt") or 0)),
            net_revenue=Decimal(str(data.get("net_revenue") or 0)),
            rank=data.get("rank"),
        )

    @property
    def discount_rate(self) -> float:
        """Discount as a percentage of gross invoice amount."""
        if not self.total_invoice_amt:
            return 0.0
        return float(self.total_discount_amt / self.total_invoice_amt * 100)

    @property
    def refund_rate(self) -> float:
        """Refund as a percentage of gross invoice amount."""
        if not self.total_invoice_amt:
            return 0.0
        return float(self.total_refund_amt / self.total_invoice_amt * 100)


@dataclass
class DealerFinancial:
    """
    Represents a single dealer financial transaction row from dlr_fin.

    Attributes:
        dealer_id: Unique dealer identifier.
        inv_amt: Gross invoice amount.
        dsc_amt: Discount applied.
        refund_amt: Refund issued.
    """

    dealer_id: str
    inv_amt: Decimal
    dsc_amt: Decimal
    refund_amt: Decimal

    @property
    def net_amount(self) -> Decimal:
        """Net amount for this transaction: inv_amt - dsc_amt - refund_amt."""
        return self.inv_amt - self.dsc_amt - self.refund_amt
