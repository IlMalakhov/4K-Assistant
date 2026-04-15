from __future__ import annotations

import psycopg
from psycopg.rows import dict_row

from Api.config import settings


def get_connection() -> psycopg.Connection:
    return psycopg.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        row_factory=dict_row,
    )


def ensure_core_schema() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS company_industry TEXT
            """
        )
        connection.commit()
