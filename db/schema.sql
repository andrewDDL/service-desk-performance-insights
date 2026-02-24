DROP TABLE IF EXISTS fact_ticket_event CASCADE;
DROP TABLE IF EXISTS fact_ticket CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;
DROP TABLE IF EXISTS dim_category CASCADE;
DROP TABLE IF EXISTS dim_group CASCADE;
DROP TABLE IF EXISTS dim_sla_policy CASCADE;
DROP TABLE IF EXISTS dim_location CASCADE;

CREATE TABLE dim_date (
    date_id INT PRIMARY KEY,
    full_date DATE,
    day INT,
    month INT,
    year INT,
    day_of_week INT,
    is_business_day BOOLEAN
);

CREATE TABLE dim_category (
    category_id SERIAL PRIMARY KEY,
    category VARCHAR,
    subcategory VARCHAR
);

CREATE TABLE dim_group (
    group_id SERIAL PRIMARY KEY,
    group_name VARCHAR,
    support_level VARCHAR
);

CREATE TABLE dim_sla_policy (
    policy_id SERIAL PRIMARY KEY,
    policy_name VARCHAR,
    default_priority_level VARCHAR,
    sla_target_hours INT
);

CREATE TABLE dim_location (
    location_id SERIAL PRIMARY KEY,
    site_name VARCHAR
);

CREATE TABLE fact_ticket_event (
    event_id UUID PRIMARY KEY,
    ticket_id VARCHAR,
    event_time TIMESTAMP,
    from_status VARCHAR,
    to_status VARCHAR,
    actor_group_id INT
);

CREATE TABLE fact_ticket (
    ticket_id VARCHAR PRIMARY KEY,
    date_id INT,
    category_id INT,
    group_id INT,
    sla_policy_id INT,
    location_id INT,
    status VARCHAR,
    created_at TIMESTAMP,
    resolved_at TIMESTAMP,
    due_at TIMESTAMP,
    breached_sla BOOLEAN,
    reopens_count INT,
    csat_score INT
);

ALTER TABLE fact_ticket
    ADD CONSTRAINT fk_fact_ticket_date
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id);

ALTER TABLE fact_ticket
    ADD CONSTRAINT fk_fact_ticket_category
    FOREIGN KEY (category_id) REFERENCES dim_category(category_id);

ALTER TABLE fact_ticket
    ADD CONSTRAINT fk_fact_ticket_group
    FOREIGN KEY (group_id) REFERENCES dim_group(group_id);

ALTER TABLE fact_ticket
    ADD CONSTRAINT fk_fact_ticket_sla_policy
    FOREIGN KEY (sla_policy_id) REFERENCES dim_sla_policy(policy_id);

ALTER TABLE fact_ticket
    ADD CONSTRAINT fk_fact_ticket_location
    FOREIGN KEY (location_id) REFERENCES dim_location(location_id);

ALTER TABLE fact_ticket_event
    ADD CONSTRAINT fk_fact_ticket_event_actor_group
    FOREIGN KEY (actor_group_id) REFERENCES dim_group(group_id);
