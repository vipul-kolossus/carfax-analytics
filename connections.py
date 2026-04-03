"""
connections.py — Database connection factory using environment variables.

All credentials are read from environment variables — never hardcoded.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_postgres_connection():
    """
    Create and return a PostgreSQL connection using environment variables.

    Environment variables required:
        WORKFORCE_CRED_FF884749_POSTGRES_CARFAX_CORE_HOST
        WORKFORCE_CRED_FF884749_POSTGRES_CARFAX_CORE_PORT
        WORKFORCE_CRED_FF884749_POSTGRES_CARFAX_CORE_DATABASE
        WORKFORCE_CRED_FF884749_POSTGRES_CARFAX_CORE_USERNAME
        WORKFORCE_CRED_FF884749_POSTGRES_CARFAX_CORE_PASSWORD
        WORKFORCE_CRED_FF884749_POSTGRES_CARFAX_CORE_SSL_MODE  (optional, default: 'require')

    Returns:
        psycopg2.connection: Active PostgreSQL connection.

    Raises:
        psycopg2.OperationalError: If connection cannot be established.
        ValueError: If required environment variables are missing.
    """
    host = os.environ.get("WORKFORCE_CRED_FF884749_POSTGRES_CARFAX_CORE_HOST")
    port = os.environ.get("WORKFORCE_CRED_FF884749_POSTGRES_CARFAX_CORE_PORT")
    database = os.environ.get("WORKFORCE_CRED_FF884749_POSTGRES_CARFAX_CORE_DATABASE")
    username = os.environ.get("WORKFORCE_CRED_FF884749_POSTGRES_CARFAX_CORE_USERNAME")
    password = os.environ.get("WORKFORCE_CRED_FF884749_POSTGRES_CARFAX_CORE_PASSWORD")
    ssl_mode = os.environ.get(
        "WORKFORCE_CRED_FF884749_POSTGRES_CARFAX_CORE_SSL_MODE", "require"
    )

    missing = [
        name
        for name, val in {
            "HOST": host,
            "PORT": port,
            "DATABASE": database,
            "USERNAME": username,
            "PASSWORD": password,
        }.items()
        if not val
    ]
    if missing:
        raise ValueError(
            f"Missing required PostgreSQL environment variables: {', '.join(missing)}"
        )

    return psycopg2.connect(
        host=host,
        port=int(port),
        dbname=database,
        user=username,
        password=password,
        sslmode=ssl_mode,
        cursor_factory=RealDictCursor,
    )
