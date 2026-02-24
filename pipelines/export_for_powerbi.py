import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
EXPORT_DIR = BASE_DIR / "data" / "exports"


def get_connection():
    load_dotenv(BASE_DIR / ".env")
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "servicedesk"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "adminpassword"),
    )


def export_query(conn, query, output_name):
    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

    df = pd.DataFrame(rows, columns=columns)
    output_path = EXPORT_DIR / output_name
    df.to_csv(output_path, index=False)
    print(f"Exported {len(df)} rows to {output_path}")


def main():
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    queries = {
        "export_tickets.csv": """
            SELECT
                ft.ticket_id,
                dd.full_date AS created_date,
                dd.day,
                dd.month,
                dd.year,
                dd.day_of_week,
                dd.is_business_day,
                dc.category,
                dc.subcategory,
                dg.group_name,
                dg.support_level,
                dsp.policy_name,
                dsp.default_priority_level,
                dsp.sla_target_hours,
                dl.site_name,
                ft.status,
                ft.created_at,
                ft.resolved_at,
                ft.due_at,
                ft.breached_sla,
                ft.reopens_count,
                ft.csat_score
            FROM fact_ticket ft
            JOIN dim_date dd
                ON dd.date_id = ft.date_id
            JOIN dim_category dc
                ON dc.category_id = ft.category_id
            JOIN dim_group dg
                ON dg.group_id = ft.group_id
            JOIN dim_sla_policy dsp
                ON dsp.policy_id = ft.sla_policy_id
            JOIN dim_location dl
                ON dl.location_id = ft.location_id
            ORDER BY ft.ticket_id
        """,
        "export_sla_compliance.csv": """
            SELECT *
            FROM vw_sla_compliance
            ORDER BY month_start, category
        """,
        "export_fcr.csv": """
            SELECT *
            FROM vw_fcr_and_escalation
            ORDER BY ticket_id
        """,
        "export_net_mttr.csv": """
            SELECT *
            FROM vw_net_mttr_events
            ORDER BY ticket_id
        """,
    }

    conn = get_connection()
    try:
        for output_name, query in queries.items():
            export_query(conn, query, output_name)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
