import os
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"


def load_env():
    load_dotenv(BASE_DIR / ".env")


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "servicedesk"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "adminpassword"),
    )


def normalize_dataframe(df):
    return df.astype(object).where(pd.notna(df), None)


def bulk_insert(df, table_name, cursor):
    if df.empty:
        print(f"Inserted 0 rows into {table_name}")
        return

    cleaned_df = normalize_dataframe(df)
    columns = list(cleaned_df.columns)
    values = [tuple(row) for row in cleaned_df.to_numpy()]
    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES %s"
    execute_values(cursor, insert_sql, values, page_size=1000)
    print(f"Inserted {len(cleaned_df)} rows into {table_name}")


def build_dim_date():
    calendar = pd.date_range(start="2024-01-01", end="2026-12-31", freq="D")
    df = pd.DataFrame({"full_date": calendar})
    df["date_id"] = df["full_date"].dt.strftime("%Y%m%d").astype(int)
    df["day"] = df["full_date"].dt.day
    df["month"] = df["full_date"].dt.month
    df["year"] = df["full_date"].dt.year
    df["day_of_week"] = df["full_date"].dt.dayofweek
    df["is_business_day"] = df["day_of_week"] < 5
    return df[["date_id", "full_date", "day", "month", "year", "day_of_week", "is_business_day"]]


def load_dataframes():
    dim_category = pd.read_csv(RAW_DIR / "dim_category.csv")
    dim_group = pd.read_csv(RAW_DIR / "dim_group.csv")
    dim_location = pd.read_csv(RAW_DIR / "dim_location.csv")
    dim_sla_policy = pd.read_csv(RAW_DIR / "dim_sla_policy.csv")
    fact_ticket = pd.read_csv(
        RAW_DIR / "fact_ticket.csv",
        parse_dates=["created_at", "resolved_at", "due_at"],
    )
    fact_ticket_event = pd.read_csv(
        RAW_DIR / "fact_ticket_event.csv",
        parse_dates=["event_time"],
    )
    return dim_category, dim_group, dim_location, dim_sla_policy, fact_ticket, fact_ticket_event


def prepare_fact_ticket(fact_ticket_df):
    df = fact_ticket_df.copy()
    df["date_id"] = df["created_at"].dt.strftime("%Y%m%d").astype(int)
    return df[
        [
            "ticket_id",
            "date_id",
            "category_id",
            "group_id",
            "sla_policy_id",
            "location_id",
            "status",
            "created_at",
            "resolved_at",
            "due_at",
            "breached_sla",
            "reopens_count",
            "csat_score",
        ]
    ]


def prepare_fact_ticket_event(fact_ticket_event_df):
    df = fact_ticket_event_df.copy()
    df["event_id"] = df["event_id"].astype(str)
    return df[
        ["event_id", "ticket_id", "event_time", "from_status", "to_status", "actor_group_id"]
    ]


def truncate_tables(cursor):
    cursor.execute(
        """
        TRUNCATE TABLE
            fact_ticket_event,
            fact_ticket,
            dim_date,
            dim_category,
            dim_group,
            dim_sla_policy,
            dim_location
        RESTART IDENTITY CASCADE
        """
    )


def main():
    load_env()
    (
        dim_category,
        dim_group,
        dim_location,
        dim_sla_policy,
        fact_ticket,
        fact_ticket_event,
    ) = load_dataframes()
    dim_date = build_dim_date()
    fact_ticket_prepared = prepare_fact_ticket(fact_ticket)
    fact_ticket_event_prepared = prepare_fact_ticket_event(fact_ticket_event)

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            truncate_tables(cursor)
            conn.commit()
            print("Truncated target tables with CASCADE")

            bulk_insert(dim_category, "dim_category", cursor)
            conn.commit()

            bulk_insert(dim_group, "dim_group", cursor)
            conn.commit()

            bulk_insert(dim_location, "dim_location", cursor)
            conn.commit()

            bulk_insert(dim_sla_policy, "dim_sla_policy", cursor)
            conn.commit()

            bulk_insert(dim_date, "dim_date", cursor)
            conn.commit()

            bulk_insert(fact_ticket_prepared, "fact_ticket", cursor)
            conn.commit()

            bulk_insert(fact_ticket_event_prepared, "fact_ticket_event", cursor)
            conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
