"""
carfax_analytics — Reusable Carfax data analytics package.

Provides parameterized query functions, territory analytics,
visualization helpers, and data models for the Carfax data platform.
"""

__version__ = "0.1.0"
__author__ = "Carfax Data Platform"

from .connections import get_postgres_connection

__all__ = ["get_postgres_connection"]
