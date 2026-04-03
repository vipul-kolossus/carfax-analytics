"""
analytics — Higher-level analytics functions built on top of raw query results.
"""

from .territory import (
    get_territory_summary,
    get_top_territories,
    get_territory_ranking,
)

__all__ = [
    "get_territory_summary",
    "get_top_territories",
    "get_territory_ranking",
]
