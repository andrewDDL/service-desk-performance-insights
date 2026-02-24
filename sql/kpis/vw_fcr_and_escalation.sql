CREATE OR REPLACE VIEW vw_fcr_and_escalation AS
-- View no nível de ticket para identificar First Contact Resolution (FCR) e escalonamento.
WITH ordered_events AS (
    -- Ordena a linha do tempo de eventos por ticket para capturar grupos inicial/final.
    SELECT
        fte.ticket_id,
        fte.actor_group_id,
        fte.event_time,
        fte.event_id,
        ROW_NUMBER() OVER (
            PARTITION BY fte.ticket_id
            ORDER BY fte.event_time ASC, fte.event_id ASC
        ) AS rn_first,
        ROW_NUMBER() OVER (
            PARTITION BY fte.ticket_id
            ORDER BY fte.event_time DESC, fte.event_id DESC
        ) AS rn_last
    FROM fact_ticket_event fte
),
initial_group AS (
    -- Grupo que tocou o ticket primeiro (esperado L1 pelo processo de abertura).
    SELECT
        ticket_id,
        actor_group_id AS initial_group_id
    FROM ordered_events
    WHERE rn_first = 1
),
final_group AS (
    -- Grupo que encerrou o fluxo do ticket (último evento na timeline).
    SELECT
        ticket_id,
        actor_group_id AS final_group_id
    FROM ordered_events
    WHERE rn_last = 1
)
SELECT
    ft.ticket_id,
    igd.group_name AS initial_group,
    fgd.group_name AS final_group,
    -- FCR verdadeiro somente quando:
    -- 1) não houve reabertura,
    -- 2) tempo total de resolução foi menor que 2 horas,
    -- 3) resolução final permaneceu no L1.
    (
        COALESCE(ft.reopens_count, 0) = 0
        AND ft.resolved_at IS NOT NULL
        AND (EXTRACT(EPOCH FROM (ft.resolved_at - ft.created_at)) / 3600.0) < 2
        AND fgd.support_level = 'L1'
    ) AS is_fcr,
    -- Escalonamento ocorre quando o grupo final difere do grupo inicial.
    (fg.final_group_id <> ig.initial_group_id) AS is_escalated
FROM fact_ticket ft
JOIN initial_group ig
    ON ig.ticket_id = ft.ticket_id
JOIN final_group fg
    ON fg.ticket_id = ft.ticket_id
JOIN dim_group igd
    ON igd.group_id = ig.initial_group_id
JOIN dim_group fgd
    ON fgd.group_id = fg.final_group_id;
