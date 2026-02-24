CREATE OR REPLACE VIEW vw_sla_compliance AS
-- KPI mensal por categoria para monitorar saúde operacional do Service Desk.
WITH resolved_tickets AS (
    -- Base apenas com tickets resolvidos/fechados para métricas de SLA e MTTR.
    SELECT
        ft.ticket_id,
        ft.created_at,
        ft.resolved_at,
        ft.breached_sla,
        dd.year,
        dd.month,
        dc.category
    FROM fact_ticket ft
    JOIN dim_date dd
        ON dd.date_id = ft.date_id
    JOIN dim_category dc
        ON dc.category_id = ft.category_id
    WHERE ft.resolved_at IS NOT NULL
),
monthly_category_rollup AS (
    -- Agrega por ano/mês/categoria para gerar os numeradores e denominadores dos KPIs.
    SELECT
        year,
        month,
        category,
        COUNT(*) AS total_tickets_resolved,
        SUM(CASE WHEN breached_sla THEN 1 ELSE 0 END) AS total_tickets_sla_breached,
        AVG(EXTRACT(EPOCH FROM (resolved_at - created_at)) / 3600.0) AS gross_mttr_hours
    FROM resolved_tickets
    GROUP BY
        year,
        month,
        category
)
SELECT
    -- Data âncora do mês para facilitar visualizações em BI.
    MAKE_DATE(year, month, 1) AS month_start,
    year,
    month,
    category,
    total_tickets_resolved,
    total_tickets_sla_breached,
    -- SLA Compliance (%) = tickets dentro do SLA / tickets resolvidos.
    ROUND(
        CASE
            WHEN total_tickets_resolved = 0 THEN 0
            ELSE (
                (total_tickets_resolved - total_tickets_sla_breached)::NUMERIC
                / total_tickets_resolved::NUMERIC
            ) * 100
        END,
        2
    ) AS sla_compliance_rate_pct,
    ROUND(gross_mttr_hours::NUMERIC, 2) AS gross_mttr_hours
FROM monthly_category_rollup
ORDER BY
    month_start,
    category;
