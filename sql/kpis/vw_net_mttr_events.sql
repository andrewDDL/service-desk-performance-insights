CREATE OR REPLACE VIEW vw_net_mttr_events AS
-- View para calcular Net MTTR por ticket removendo tempo em Pending.
WITH ordered_events AS (
    -- Para cada evento, capturamos o próximo evento cronológico do mesmo ticket.
    -- Isso permite parear automaticamente as transições de entrada/saída de Pending.
    SELECT
        fte.ticket_id,
        fte.event_id,
        fte.event_time,
        fte.from_status,
        fte.to_status,
        LEAD(fte.event_time) OVER (
            PARTITION BY fte.ticket_id
            ORDER BY fte.event_time, fte.event_id
        ) AS next_event_time,
        LEAD(fte.from_status) OVER (
            PARTITION BY fte.ticket_id
            ORDER BY fte.event_time, fte.event_id
        ) AS next_from_status,
        LEAD(fte.to_status) OVER (
            PARTITION BY fte.ticket_id
            ORDER BY fte.event_time, fte.event_id
        ) AS next_to_status
    FROM fact_ticket_event fte
),
pending_intervals AS (
    -- Intervalos válidos de Pending:
    -- evento atual = In Progress -> Pending
    -- próximo evento = Pending -> In Progress
    SELECT
        ticket_id,
        EXTRACT(EPOCH FROM (next_event_time - event_time)) / 3600.0 AS pending_hours
    FROM ordered_events
    WHERE from_status = 'In Progress'
      AND to_status = 'Pending'
      AND next_from_status = 'Pending'
      AND next_to_status = 'In Progress'
      AND next_event_time IS NOT NULL
),
pending_rollup AS (
    -- Soma todas as pausas de Pending por ticket.
    SELECT
        ticket_id,
        SUM(pending_hours) AS total_pending_hours
    FROM pending_intervals
    GROUP BY ticket_id
)
SELECT
    ft.ticket_id,
    COALESCE(ROUND(pr.total_pending_hours::NUMERIC, 2), 0::NUMERIC) AS total_pending_hours
FROM fact_ticket ft
LEFT JOIN pending_rollup pr
    ON pr.ticket_id = ft.ticket_id;
