import pandas as pd
from faker import Faker
import uuid
import random
from datetime import datetime, timedelta


RAW_DATA_DIR = "data/raw"


def generate_dim_category():
    data = [
        {"category_id": 1, "category": "Network", "subcategory": "VPN"},
        {"category_id": 2, "category": "Network", "subcategory": "Wi-Fi"},
        {"category_id": 3, "category": "Hardware", "subcategory": "Laptop"},
        {"category_id": 4, "category": "Hardware", "subcategory": "Desktop"},
        {"category_id": 5, "category": "Access/Identity", "subcategory": "Password Reset"},
        {"category_id": 6, "category": "Access/Identity", "subcategory": "MFA"},
        {"category_id": 7, "category": "Software", "subcategory": "ERP"},
        {"category_id": 8, "category": "Software", "subcategory": "Office Suite"},
    ]
    df = pd.DataFrame(data)
    df.to_csv(f"{RAW_DATA_DIR}/dim_category.csv", index=False)
    return df


def generate_dim_group():
    data = [
        {"group_id": 1, "group_name": "L1 Helpdesk", "support_level": "L1"},
        {"group_id": 2, "group_name": "L2 Infra", "support_level": "L2"},
        {"group_id": 3, "group_name": "L2 Apps", "support_level": "L2"},
        {"group_id": 4, "group_name": "L3 Engineering", "support_level": "L3"},
    ]
    df = pd.DataFrame(data)
    df.to_csv(f"{RAW_DATA_DIR}/dim_group.csv", index=False)
    return df


def generate_dim_location():
    data = [
        {"location_id": 1, "site_name": "Matriz SP"},
        {"location_id": 2, "site_name": "Filial RJ"},
        {"location_id": 3, "site_name": "Filial MG"},
        {"location_id": 4, "site_name": "Remote"},
    ]
    df = pd.DataFrame(data)
    df.to_csv(f"{RAW_DATA_DIR}/dim_location.csv", index=False)
    return df


def generate_dim_sla_policy():
    data = [
        {"policy_id": 1, "policy_name": "P1", "default_priority_level": "P1", "sla_target_hours": 4},
        {"policy_id": 2, "policy_name": "P2", "default_priority_level": "P2", "sla_target_hours": 8},
        {"policy_id": 3, "policy_name": "P3", "default_priority_level": "P3", "sla_target_hours": 24},
        {"policy_id": 4, "policy_name": "P4", "default_priority_level": "P4", "sla_target_hours": 48},
    ]
    df = pd.DataFrame(data)
    df.to_csv(f"{RAW_DATA_DIR}/dim_sla_policy.csv", index=False)
    return df


def random_datetime_last_12_months(reference_time):
    start = reference_time - timedelta(days=365)
    end = reference_time - timedelta(days=2)
    total_seconds = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, total_seconds))


def add_event(events, ticket_id, event_time, from_status, to_status, actor_group_id):
    events.append(
        {
            "event_id": str(uuid.uuid4()),
            "ticket_id": ticket_id,
            "event_time": event_time,
            "from_status": from_status,
            "to_status": to_status,
            "actor_group_id": actor_group_id,
        }
    )


def choose_resolution_target_hours(sla_target_hours, should_breach, has_pending):
    if should_breach:
        return random.uniform(1.10 * sla_target_hours, 1.45 * sla_target_hours)

    lower_bound = 0.35 * sla_target_hours
    if has_pending:
        # Pending tem pausa minima de 2h, entao precisa de duracao minima viavel.
        lower_bound = max(lower_bound, 2.5)

    upper_bound = 0.88 * sla_target_hours
    if lower_bound >= upper_bound:
        lower_bound = max(0.2, upper_bound - 0.1)

    return random.uniform(lower_bound, upper_bound)


def generate_fact_ticket_event(fake, dim_category, dim_group, dim_location, dim_sla_policy):
    ticket_count = random.randint(3000, 5000)
    now = datetime.now()
    events = []
    ticket_attributes = []
    sla_hours_map = dict(zip(dim_sla_policy["policy_id"], dim_sla_policy["sla_target_hours"]))

    ticket_numbers = list(range(1, ticket_count + 1))
    breach_target_count = int(round(ticket_count * random.uniform(0.10, 0.15)))
    pending_target_count = int(round(ticket_count * 0.20))
    reopen_target_count = int(round(ticket_count * 0.10))

    breach_ticket_numbers = set(random.sample(ticket_numbers, breach_target_count))
    pending_ticket_numbers = set(random.sample(ticket_numbers, pending_target_count))
    reopen_ticket_numbers = set(random.sample(ticket_numbers, reopen_target_count))

    for i in ticket_numbers:
        ticket_id = f"TCK-{i:06d}"
        created_at = random_datetime_last_12_months(now)

        category_id = random.choice(dim_category["category_id"].tolist())
        group_id = random.choices([1, 2, 3, 4], weights=[0.5, 0.2, 0.2, 0.1], k=1)[0]
        location_id = random.choice(dim_location["location_id"].tolist())
        sla_policy_id = random.choices([1, 2, 3, 4], weights=[0.1, 0.25, 0.4, 0.25], k=1)[0]
        sla_target_hours = sla_hours_map[sla_policy_id]

        ticket_attributes.append(
            {
                "ticket_id": ticket_id,
                "category_id": category_id,
                "group_id": group_id,
                "sla_policy_id": sla_policy_id,
                "location_id": location_id,
                "requester_name": fake.name(),
                "subject": fake.sentence(nb_words=6),
            }
        )

        should_breach = i in breach_ticket_numbers
        has_pending = i in pending_ticket_numbers
        has_reopen = i in reopen_ticket_numbers

        target_resolution_hours = choose_resolution_target_hours(
            sla_target_hours=sla_target_hours,
            should_breach=should_breach,
            has_pending=has_pending,
        )
        final_resolve_time = created_at + timedelta(hours=target_resolution_hours)

        # Event sourcing: estado final e sempre derivado do fluxo de eventos.
        add_event(events, ticket_id, created_at, None, "New", 1)

        new_to_in_progress_hours = min(
            random.uniform(0.05, 0.25),
            max(0.02, target_resolution_hours * 0.20),
        )
        in_progress_time = created_at + timedelta(hours=new_to_in_progress_hours)
        if in_progress_time >= final_resolve_time:
            in_progress_time = created_at + timedelta(hours=max(0.01, target_resolution_hours * 0.1))

        add_event(events, ticket_id, in_progress_time, "New", "In Progress", group_id)
        current_time = in_progress_time

        # Regra atomica do Pending: entrada e saida imediata como dois eventos consecutivos.
        if has_pending:
            remaining_hours = (final_resolve_time - current_time).total_seconds() / 3600.0
            min_after_pending_hours = 0.25 if has_reopen else 0.10
            pre_pending_min = 0.05
            pre_pending_max = min(0.4, remaining_hours - 2.0 - min_after_pending_hours)

            if pre_pending_max >= pre_pending_min:
                pre_pending_hours = random.uniform(pre_pending_min, pre_pending_max)
                pending_max = min(48.0, remaining_hours - pre_pending_hours - min_after_pending_hours)

                if pending_max >= 2.0:
                    pending_hours = random.uniform(2.0, pending_max)
                    pending_start = current_time + timedelta(hours=pre_pending_hours)
                    pending_end = pending_start + timedelta(hours=pending_hours)

                    add_event(events, ticket_id, pending_start, "In Progress", "Pending", group_id)
                    add_event(events, ticket_id, pending_end, "Pending", "In Progress", group_id)
                    current_time = pending_end

        remaining_hours = (final_resolve_time - current_time).total_seconds() / 3600.0
        if has_reopen and remaining_hours > 0.20:
            first_resolved_ratio = random.uniform(0.45, 0.80)
            first_resolved_time = current_time + timedelta(hours=remaining_hours * first_resolved_ratio)
            remaining_after_first = (final_resolve_time - first_resolved_time).total_seconds() / 3600.0
            reopen_gap_max = min(2.0, remaining_after_first - 0.05)

            if reopen_gap_max >= 0.05:
                reopen_gap_hours = random.uniform(0.05, reopen_gap_max)
                reopen_time = first_resolved_time + timedelta(hours=reopen_gap_hours)

                add_event(events, ticket_id, first_resolved_time, "In Progress", "Resolved", group_id)
                add_event(events, ticket_id, reopen_time, "Resolved", "In Progress", group_id)
                add_event(events, ticket_id, final_resolve_time, "In Progress", "Resolved", group_id)
            else:
                add_event(events, ticket_id, final_resolve_time, "In Progress", "Resolved", group_id)
        else:
            add_event(events, ticket_id, final_resolve_time, "In Progress", "Resolved", group_id)

        close_time = final_resolve_time + timedelta(hours=random.uniform(0.25, 24))
        add_event(events, ticket_id, close_time, "Resolved", "Closed", group_id)

    events_df = pd.DataFrame(events)
    events_df["event_time"] = pd.to_datetime(events_df["event_time"])
    events_df = events_df.sort_values(["ticket_id", "event_time"]).reset_index(drop=True)
    events_df.to_csv(f"{RAW_DATA_DIR}/fact_ticket_event.csv", index=False)

    ticket_attributes_df = pd.DataFrame(ticket_attributes)
    return events_df, ticket_attributes_df


def calculate_csat_score(reopens_count, breached_sla):
    if reopens_count > 0 or breached_sla:
        return random.choices([1, 2, 3, 4, 5], weights=[0.34, 0.28, 0.2, 0.12, 0.06], k=1)[0]
    return random.choices([1, 2, 3, 4, 5], weights=[0.06, 0.09, 0.2, 0.3, 0.35], k=1)[0]


def build_fact_ticket(events_df, ticket_attributes_df, dim_sla_policy):
    # Projecao materializada: consolida o snapshot final a partir dos eventos.
    ticket_rows = []
    sla_hours_map = dict(zip(dim_sla_policy["policy_id"], dim_sla_policy["sla_target_hours"]))

    for ticket_id, group in events_df.groupby("ticket_id"):
        ordered = group.sort_values("event_time")
        attributes = ticket_attributes_df.loc[ticket_attributes_df["ticket_id"] == ticket_id].iloc[0]

        created_at = ordered.loc[ordered["to_status"] == "New", "event_time"].min()
        resolved_at = ordered.loc[ordered["to_status"] == "Resolved", "event_time"].max()
        final_status = ordered["to_status"].iloc[-1]
        reopens_count = ((ordered["from_status"] == "Resolved") & (ordered["to_status"] == "In Progress")).sum()

        sla_hours = sla_hours_map[int(attributes["sla_policy_id"])]
        due_at = created_at + timedelta(hours=sla_hours)
        breached_sla = bool(pd.notna(resolved_at) and resolved_at > due_at)

        csat_score = None
        if pd.notna(resolved_at):
            csat_score = calculate_csat_score(reopens_count, breached_sla)

        ticket_rows.append(
            {
                "ticket_id": ticket_id,
                "date_id": int(created_at.strftime("%Y%m%d")),
                "category_id": int(attributes["category_id"]),
                "group_id": int(attributes["group_id"]),
                "sla_policy_id": int(attributes["sla_policy_id"]),
                "location_id": int(attributes["location_id"]),
                "status": final_status,
                "created_at": created_at,
                "resolved_at": resolved_at,
                "due_at": due_at,
                "breached_sla": breached_sla,
                "reopens_count": int(reopens_count),
                "csat_score": csat_score,
            }
        )

    fact_ticket_df = pd.DataFrame(ticket_rows).sort_values("ticket_id").reset_index(drop=True)
    fact_ticket_df.to_csv(f"{RAW_DATA_DIR}/fact_ticket.csv", index=False)
    return fact_ticket_df


def main():
    random.seed(42)
    Faker.seed(42)
    fake = Faker("pt_BR")

    dim_category = generate_dim_category()
    dim_group = generate_dim_group()
    dim_location = generate_dim_location()
    dim_sla_policy = generate_dim_sla_policy()

    events_df, ticket_attributes_df = generate_fact_ticket_event(
        fake=fake,
        dim_category=dim_category,
        dim_group=dim_group,
        dim_location=dim_location,
        dim_sla_policy=dim_sla_policy,
    )

    fact_ticket_df = build_fact_ticket(
        events_df=events_df,
        ticket_attributes_df=ticket_attributes_df,
        dim_sla_policy=dim_sla_policy,
    )

    print(f"CSV files generated in {RAW_DATA_DIR}")
    print(f"fact_ticket_event rows: {len(events_df)}")
    print(f"fact_ticket rows: {len(fact_ticket_df)}")


if __name__ == "__main__":
    main()
