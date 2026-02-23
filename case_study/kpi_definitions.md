# KPI Definitions & Business Logic

This document defines the core metrics used in the Service Desk Performance Insights project. To ensure data integrity, especially for complex metrics like Net MTTR, this project utilizes an Event Sourcing approach.

## SLA Compliance Rate
* **Definition:** The percentage of tickets resolved within their agreed-upon Service Level Agreement (SLA) target.
* **Calculation:** `(Count of Tickets where resolved_at <= due_at) / (Total Resolved Tickets) * 100`
* **Business Rule:** The `due_at` timestamp is calculated at the moment of ticket creation based on the `dim_sla_policy`. The SLA clock pauses while a ticket is in the `Pending` status (awaiting user response).

## Gross MTTR vs Net MTTR
* **Gross Mean Time to Resolve (MTTR):** The total elapsed calendar time from ticket creation to resolution.
  * *Formula:* `Average(resolved_at - created_at)`
  * *Purpose:* Measures the user's perception of how long the issue took to be fixed.
* **Net MTTR:** The actual time the support team spent actively working on the ticket.
  * *Formula:* `Average((resolved_at - created_at) - Total Pending Time)`
  * *Purpose:* Measures the true operational efficiency of the Service Desk by excluding time blocked by external factors.

## First Contact Resolution (FCR) Proxy
* **Definition:** The percentage of issues resolved during the user's initial interaction with the Level 1 support team.
* **Calculation:** A ticket is flagged as FCR if it meets ALL the following criteria:
  1. Resolved by the L1 Helpdesk group.
  2. Total Gross Time is less than 2 hours.
  3. `reopens_count = 0` (Never transitioned from Resolved back to In Progress).
  4. No escalation occurred (the `actor_group_id` remained L1).

## Escalation Rate
* **Definition:** The percentage of tickets that required reassignment from the initial triage tier (L1) to specialized tiers (L2 or L3).
* **Calculation:** `(Count of tickets where final group != initial group) / (Total Tickets) * 100`
