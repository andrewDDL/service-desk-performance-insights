# Data Dictionary (Star Schema)

The data warehouse is built on a PostgreSQL database using a dimensional model optimized for ITSM analytics.

## Fact Tables

### `fact_ticket_event`
The primary source of truth. Records every state transition to mathematically guarantee accurate MTTR and workflow analysis.
* `event_id` (PK, UUID): Unique identifier for the event.
* `ticket_id` (FK, String): Reference to the ticket.
* `event_time` (Timestamp): Exact time the transition occurred.
* `from_status` (String): Previous status (NULL for the first event).
* `to_status` (String): New status.
* `actor_group_id` (FK, Int): The support group responsible for the transition.

### `fact_ticket`
A materialized view/table derived entirely from `fact_ticket_event`. Represents the final state of the ticket.
* `ticket_id` (PK, String): Unique identifier.
* `date_id` (FK, Int): Reference to the creation date.
* `category_id` (FK, Int): Reference to the issue category.
* `group_id` (FK, Int): Reference to the *last* group assigned.
* `sla_policy_id` (FK, Int): Reference to the applied SLA policy.
* `location_id` (FK, Int): Reference to the requester's location.
* `status` (String): Current status.
* `created_at` (Timestamp): Derived from the first event.
* `resolved_at` (Timestamp): Derived from the last 'Resolved' event.
* `due_at` (Timestamp): Calculated target resolution time.
* `breached_sla` (Boolean): True if resolved_at > due_at.
* `reopens_count` (Int): Count of (Resolved -> In Progress) events.
* `csat_score` (Int): Customer Satisfaction Score (1-5), nullable.

## Dimension Tables
* **`dim_date`**: Calendar dimension with `is_business_day` flag.
* **`dim_category`**: Hierarchical classification (`category`, `subcategory`).
* **`dim_group`**: Support tiers (`group_name`, `support_level`).
* **`dim_sla_policy`**: Policy details (`policy_name`, `default_priority_level`, `sla_target_hours`).
* **`dim_location`**: Geographic tracking (`site_name`).
