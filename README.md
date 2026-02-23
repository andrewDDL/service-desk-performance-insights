# Service Desk Performance Insights

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](#)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
[![Power_BI](https://img.shields.io/badge/Power_BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)](#)

## Overview | Visão Geral

### English
This project is an end-to-end data engineering and analytics portfolio designed to simulate a realistic IT Service Management (ITSM) operation. It translates raw technical support events into actionable business metrics.

The goal is to demonstrate practical competency in **ITIL/ITSM processes**, **dimensional data modeling (Star Schema)**, and **business intelligence**. By generating a realistic dataset of 5,000+ support tickets and processing them through a complete data pipeline, this project answers critical operational questions:
* What is the true operational efficiency (**Net MTTR**) when isolating user wait times?
* What is the actual SLA compliance rate across different priorities and categories?
* How effectively is the Level 1 team resolving issues at first contact (**FCR Proxy**)?

### Português (Brasil)
Este projeto é um portfólio end-to-end de engenharia e análise de dados, desenvolvido para simular uma operação realista de IT Service Management (ITSM). Ele transforma eventos brutos de suporte técnico em métricas de negócio acionáveis.

O objetivo é demonstrar competência prática em **processos ITIL/ITSM**, **modelagem dimensional de dados (Star Schema)** e **business intelligence**. Ao gerar um dataset realista com mais de 5.000 tickets de suporte e processá-lo por um pipeline completo de dados, este projeto responde a perguntas operacionais críticas:
* Qual é a eficiência operacional real (**Net MTTR**) ao isolar tempos de espera do usuário?
* Qual é a taxa real de conformidade com SLA entre diferentes prioridades e categorias?
* Quão efetivamente o time de Nível 1 resolve incidentes no primeiro contato (**FCR Proxy**)?

## Architecture & Methodology | Arquitetura e Metodologia

### English
The core differentiator of this project is the use of the **Event Sourcing** paradigm for data generation and modeling.

Instead of merely generating a flat table of tickets, the Python pipeline acts as a state machine:
1. **`fact_ticket_event`**: Generates the exact chronological history of status transitions (e.g., *New -> In Progress -> Pending -> In Progress -> Resolved*).
2. **`fact_ticket`**: This final table is strictly derived from the event history.

This approach mirrors enterprise systems like ServiceNow or Jira and mathematically guarantees the integrity of complex KPIs, such as pausing the SLA clock while a ticket is awaiting user input.

### Português (Brasil)
O principal diferencial deste projeto é o uso do paradigma de **Event Sourcing** para geração e modelagem de dados.

Em vez de gerar apenas uma tabela plana de tickets, o pipeline em Python funciona como uma máquina de estados:
1. **`fact_ticket_event`**: Gera o histórico cronológico exato das transições de status (ex.: *New -> In Progress -> Pending -> In Progress -> Resolved*).
2. **`fact_ticket`**: Esta tabela final é derivada estritamente do histórico de eventos.

Essa abordagem espelha sistemas corporativos como ServiceNow ou Jira e garante matematicamente a integridade de KPIs complexos, como pausar o relógio de SLA enquanto um ticket aguarda retorno do usuário.

## Tech Stack | Stack Tecnológica
* **Data Generation & Pipeline / Geração de Dados e Pipeline:** Python (Pandas, Faker)
* **Storage & Data Warehouse / Armazenamento e Data Warehouse:** PostgreSQL (containerizado via Docker)
* **Transformations & KPIs / Transformações e KPIs:** SQL (CTEs, Window Functions, Aggregations)
* **Visualization / Visualização:** Power BI (dashboards executivos e operacionais)
* **Tactical Operations / Operação Tática:** Excel (Ops Pack para acompanhamento diário)

## Repository Structure | Estrutura do Repositório
* `/case_study/`: Business-focused documentation detailing the problem, approach, and executive findings. / Documentação orientada ao negócio com problema, abordagem e achados executivos.
* `/docs/`: Technical documentation including the Data Dictionary and Architecture. / Documentação técnica, incluindo Data Dictionary e Arquitetura.
* `/pipelines/`: Python scripts for generating the synthetic state-machine dataset and loading it into Postgres. / Scripts Python para gerar o dataset sintético baseado em máquina de estados e carregar no Postgres.
* `/sql/`: DDL schemas, data marts, and KPI queries. / Schemas DDL, data marts e consultas de KPI.
* `/powerbi/`: The final interactive dashboard file. / Arquivo final do dashboard interativo.

## How to Run (Local Environment) | Como Executar (Ambiente Local)

### English
This project is designed to be 100% reproducible locally using Docker and Make.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/andrewDDL/service-desk-performance-insights.git
   cd service-desk-performance-insights
   ```
2. **Prepare environment variables:**
   ```bash
   cp .env.example .env
   ```
3. **Run pipeline and analytics steps:**
   *Detailed execution commands will be documented as pipeline scripts and SQL modules are added.*

### Português (Brasil)
Este projeto foi desenhado para ser 100% reproduzível localmente usando Docker e Make.

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/andrewDDL/service-desk-performance-insights.git
   cd service-desk-performance-insights
   ```
2. **Prepare as variáveis de ambiente:**
   ```bash
   cp .env.example .env
   ```
3. **Execute as etapas de pipeline e análise:**
   *Os comandos detalhados serão documentados conforme os scripts de pipeline e módulos SQL forem adicionados.*
