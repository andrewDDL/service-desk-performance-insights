# Dicionário de KPIs - Service Desk Performance Insights

Este documento consolida as definições dos principais indicadores da operação de Service Desk, com base nas regras implementadas nas views SQL analíticas e nas medidas do dashboard.

## 1. Indicadores de SLA e Eficiência Temporal

### 1.1 SLA Compliance Rate (%)
- **Nome do KPI:** SLA Compliance Rate (%)
- **Descrição:** Percentual de tickets resolvidos dentro do prazo definido pela política de SLA.
- **Lógica de Cálculo (DAX/SQL):**
  - **Base SQL (view `vw_sla_compliance`):**
    - `total_tickets_resolved = COUNT(*)` com `resolved_at IS NOT NULL`
    - `total_tickets_sla_breached = SUM(CASE WHEN breached_sla THEN 1 ELSE 0 END)`
    - `sla_compliance_rate_pct = ((total_tickets_resolved - total_tickets_sla_breached) / total_tickets_resolved) * 100`
  - **Equivalente DAX (conceitual):**
    - `SLA Compliance % = DIVIDE([Tickets Resolvidos no Prazo], [Tickets Resolvidos], 0) * 100`
- **Impacto no Negócio:** Suporta gestão de risco de contrato, priorização de melhorias por categoria e controle de performance de atendimento frente a metas de nível de serviço.

### 1.2 Gross MTTR (Mean Time to Resolve - Horas)
- **Nome do KPI:** Gross MTTR (Horas)
- **Descrição:** Tempo médio bruto de resolução, considerando o ciclo completo entre abertura e resolução.
- **Lógica de Cálculo (DAX/SQL):**
  - **Base SQL (view `vw_sla_compliance`):**
    - `gross_mttr_hours = AVG(EXTRACT(EPOCH FROM (resolved_at - created_at)) / 3600.0)`
    - Aplicado apenas a tickets com `resolved_at IS NOT NULL`
  - **Equivalente DAX (conceitual):**
    - `Gross MTTR (h) = AVERAGEX(TicketsResolvidos, DATEDIFF(created_at, resolved_at, SECOND) / 3600)`
- **Impacto no Negócio:** Representa a percepção de tempo total do usuário e orienta decisões de capacidade operacional, SLA e priorização de filas.

### 1.3 Net MTTR (Horas)
- **Nome do KPI:** Net MTTR (Horas)
- **Descrição:** Tempo médio líquido de resolução, refletindo o esforço real do time ao desconsiderar períodos de espera em `Pending`.
- **Lógica de Cálculo (DAX/SQL):**
  - **Base SQL de tempo em pausa (view `vw_net_mttr_events`):**
    - Pareamento de eventos `In Progress -> Pending` com o próximo `Pending -> In Progress` via `LEAD()`
    - `total_pending_hours = SUM(EXTRACT(EPOCH FROM (next_event_time - event_time)) / 3600.0)` por `ticket_id`
  - **Composição do KPI:**
    - `Net MTTR = Gross MTTR - Tempo em Pending`
    - Em nível de ticket: `(resolved_at - created_at em horas) - total_pending_hours`
  - **Equivalente DAX (conceitual):**
    - `Net MTTR (h) = AVERAGEX(TicketsResolvidos, [Gross MTTR Ticket (h)] - [Tempo Pending Ticket (h)])`
- **Impacto no Negócio:** Separa ineficiência interna de espera externa, permitindo planos de ação mais precisos para produtividade técnica e governança de processo.

### 1.4 Tempo em Pending (Horas)
- **Nome do KPI:** Tempo em Pending (Horas)
- **Descrição:** Quantidade de horas em que o ticket ficou pausado aguardando retorno de usuário, fornecedor ou terceiro.
- **Lógica de Cálculo (DAX/SQL):**
  - **Base SQL (view `vw_net_mttr_events`):**
    - Captura intervalos válidos:
      - evento atual: `from_status = 'In Progress'` e `to_status = 'Pending'`
      - próximo evento: `from_status = 'Pending'` e `to_status = 'In Progress'`
    - `pending_hours = EXTRACT(EPOCH FROM (next_event_time - event_time)) / 3600.0`
    - `total_pending_hours = SUM(pending_hours)` por ticket
  - **Agregações usuais no BI:**
    - `SUM(total_pending_hours)` (volume total)
    - `AVG(total_pending_hours)` (média por ticket)
- **Impacto no Negócio:** Identifica gargalos de espera fora da atuação técnica direta e orienta políticas de follow-up, comunicação e automação de pendências.

## 2. Indicadores de Resolução e Escalonamento

### 2.1 FCR Rate (First Contact Resolution - %)
- **Nome do KPI:** FCR Rate (%)
- **Descrição:** Percentual de tickets resolvidos no primeiro contato, sem reabertura e com resolução final no Nível 1.
- **Lógica de Cálculo (DAX/SQL):**
  - **Base SQL (view `vw_fcr_and_escalation`):**
    - `is_fcr = TRUE` quando:
      - `reopens_count = 0`
      - `resolved_at IS NOT NULL`
      - `(resolved_at - created_at) < 2 horas`
      - grupo final com `support_level = 'L1'`
  - **Taxa no BI:**
    - `FCR Rate % = COUNT(is_fcr = TRUE) / COUNT(total de tickets) * 100`
- **Impacto no Negócio:** Mede efetividade do Nível 1, reduz custo por chamado e influencia diretamente experiência do usuário e tempo de resposta.

### 2.2 Escalation Rate (%)
- **Nome do KPI:** Escalation Rate (%)
- **Descrição:** Percentual de tickets abertos no L1 que precisaram de repasse para níveis superiores.
- **Lógica de Cálculo (DAX/SQL):**
  - **Base SQL (view `vw_fcr_and_escalation`):**
    - `is_escalated = (final_group_id <> initial_group_id)`
  - **Taxa no BI (foco em origem L1):**
    - `Escalation Rate % = COUNT(initial_group = 'L1 Helpdesk' AND is_escalated = TRUE) / COUNT(initial_group = 'L1 Helpdesk') * 100`
- **Impacto no Negócio:** Apoia decisões sobre maturidade de triagem, necessidade de treinamento no L1 e balanceamento entre N1, N2 e N3.

## 3. Indicadores de Qualidade Percebida e Carteira Ativa

### 3.1 CSAT Médio (Customer Satisfaction Score)
- **Nome do KPI:** CSAT Médio (1 a 5)
- **Descrição:** Média das notas de satisfação dos usuários em tickets finalizados com pesquisa respondida.
- **Lógica de Cálculo (DAX/SQL):**
  - **Regra de dados:**
    - `csat_score` é preenchido apenas quando há resolução (`resolved_at IS NOT NULL`)
  - **Cálculo:**
    - `CSAT Médio = AVG(csat_score)` considerando `csat_score IS NOT NULL`
    - Escala: `1` (muito insatisfeito) a `5` (muito satisfeito)
- **Impacto no Negócio:** Indica percepção de valor do serviço e direciona ações de melhoria em atendimento, comunicação e qualidade técnica por categoria/grupo.

### 3.2 Backlog Ativo
- **Nome do KPI:** Backlog Ativo
- **Descrição:** Volume de tickets ainda em andamento e que exigem atuação operacional.
- **Lógica de Cálculo (DAX/SQL):**
  - `Backlog Ativo = COUNT(tickets com status IN ('New', 'In Progress', 'Pending'))`
  - Exclui tickets em `Closed` e `Resolved`
- **Impacto no Negócio:** Suporta decisões de alocação de equipe, priorização diária e controle de risco de envelhecimento da fila.
