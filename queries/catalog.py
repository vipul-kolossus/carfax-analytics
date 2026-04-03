"""
catalog.py — Semantic catalog query functions.

Provides access to the Business Glossary, table columns, and
table relationships stored in the carfax_catalog schema.
"""

from typing import List, Dict, Any, Optional
from ..connections import get_postgres_connection


def get_glossary_terms(
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve terms from the Business Glossary.

    Args:
        category: Optional category filter (e.g., 'finance', 'revenue', 'kpi').
        search: Optional keyword to search within term names and definitions.

    Returns:
        List of dicts with keys: term, definition, category, related_tables, related_columns.

    Example:
        >>> terms = get_glossary_terms(category='finance')
        >>> terms = get_glossary_terms(search='revenue')
    """
    conditions = []
    params: Dict[str, Any] = {}

    if category:
        conditions.append("lower(category) = lower(%(category)s)")
        params["category"] = category
    if search:
        conditions.append(
            "(lower(term) LIKE lower(%(search)s) OR lower(definition) LIKE lower(%(search)s))"
        )
        params["search"] = f"%{search}%"

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    sql = f"""
        SELECT term, definition, category, related_tables, related_columns
        FROM carfax_catalog.catalog_glossary
        {where_clause}
        ORDER BY term
    """

    conn = get_postgres_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def get_table_columns(
    schema_name: str,
    table_name: str,
) -> List[Dict[str, Any]]:
    """
    Return column metadata for a given table from the semantic catalog.

    Args:
        schema_name: Database schema name (e.g., 'carfax_operations').
        table_name: Table name (e.g., 'dlr_fin').

    Returns:
        List of dicts with keys:
            column_name, data_type, inferred_description, is_pk, is_fk, fk_ref_table.

    Example:
        >>> cols = get_table_columns('carfax_operations', 'dlr_fin')
    """
    sql = """
        SELECT
            cc.column_name,
            cc.data_type,
            cc.inferred_description,
            cc.is_pk,
            cc.is_fk,
            cc.fk_ref_table
        FROM carfax_catalog.catalog_columns cc
        JOIN carfax_catalog.catalog_tables ct
            ON cc.catalog_table_id = ct.id
        WHERE ct.schema_name = %(schema_name)s
          AND ct.table_name  = %(table_name)s
        ORDER BY cc.id
    """
    conn = get_postgres_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, {"schema_name": schema_name, "table_name": table_name})
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def get_table_relationships(
    table_name: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Return join relationships from the semantic catalog.

    Args:
        table_name: Optional table name filter. If provided, returns relationships
                    where this table appears as source or target.

    Returns:
        List of relationship dicts from catalog_relationships.

    Example:
        >>> rels = get_table_relationships()
        >>> rels = get_table_relationships(table_name='dlr_fin')
    """
    where_clause = ""
    params: Dict[str, Any] = {}

    if table_name:
        where_clause = """
            WHERE lower(source_table) LIKE lower(%(pattern)s)
               OR lower(target_table) LIKE lower(%(pattern)s)
        """
        params["pattern"] = f"%{table_name}%"

    sql = f"""
        SELECT *
        FROM carfax_catalog.catalog_relationships
        {where_clause}
        ORDER BY source_table, target_table
    """

    conn = get_postgres_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()
