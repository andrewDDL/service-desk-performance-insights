# Architecture & Methodology

## System Overview
This project simulates a fully functional ITSM data pipeline. Data is generated synthetically via a Python engine (Pandas, Faker), loaded into a Dockerized PostgreSQL Data Warehouse, and visualized in Power BI.

## The Event Sourcing Approach
Traditional ITSM datasets often rely on flat tables, making it mathematically impossible to accurately calculate metrics like "Net MTTR" if a ticket enters a "Pending" state multiple times. 

To solve this, we use an **Event Sourcing** pattern:
1. The Python generator acts as a state machine, strictly writing to the `fact_ticket_event` table first.
2. The `fact_ticket` table is mathematically derived from the event history.
3. This ensures chronological integrity and mirrors real-world enterprise databases (e.g., ServiceNow task_sla engines).

## Handling State Transitions (The 'Pending' Pause)
The state machine strictly adheres to valid transitions: `New → In Progress → [Pending] → Resolved → Closed`. 
To ensure data integrity, any transition into `Pending` is treated as an atomic block: the script generates the `In Progress → Pending` event and immediately calculates and inserts the `Pending → In Progress` return event. This prevents orphaned states and ensures accurate Net MTTR calculation.

## Pipeline Flow
1. **Generate (`make generate`):** Python script produces raw CSVs applying business rules (seasonality, SLA targets).
2. **Load (`make load`):** Python connects via `psycopg2` to execute bulk inserts into the Postgres Star Schema.
3. **Analyze:** SQL Views calculate complex aggregations, which are then consumed by Power BI via DirectQuery or Import mode.
