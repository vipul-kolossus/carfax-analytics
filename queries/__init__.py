"""
queries — Parameterized SQL query functions for the Carfax data platform.
"""

from .net_revenue import get_net_revenue_by_territory
from .catalog import get_glossary_terms, get_table_columns, get_table_relationships

__all__ = [
    "get_net_revenue_by_territory",
    "get_glossary_terms",
    "get_table_columns",
    "get_table_relationships",
]
