import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
SQL_DIR = BASE_DIR / "sql" / "kpis"


def get_connection():
    load_dotenv(BASE_DIR / ".env")
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "servicedesk"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "adminpassword"),
    )


def execute_sql_file(cursor, file_path):
    sql_text = file_path.read_text(encoding="utf-8")
    cursor.execute(sql_text)
    print(f"Executed: {file_path.name}")


def main():
    sql_files = [
        SQL_DIR / "vw_sla_compliance.sql",
        SQL_DIR / "vw_fcr_and_escalation.sql",
        SQL_DIR / "vw_net_mttr_events.sql",
    ]

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            for sql_file in sql_files:
                execute_sql_file(cursor, sql_file)
                conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
