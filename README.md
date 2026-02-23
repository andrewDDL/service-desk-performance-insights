# Service Desk Performance Insights

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](#)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
[![Power_BI](https://img.shields.io/badge/Power_BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)](#)

## Overview | Visao Geral

### English
This project is an end-to-end data engineering and analytics portfolio designed to simulate a realistic IT Service Management (ITSM) operation. It translates raw technical support events into actionable business metrics.

The goal is to demonstrate practical competency in **ITIL/ITSM processes**, **dimensional data modeling (Star Schema)**, and **business intelligence**. By generating a realistic dataset of 5,000+ support tickets and processing them through a complete data pipeline, this project answers critical operational questions:
* What is the true operational efficiency (**Net MTTR**) when isolating user wait times?
* What is the actual SLA compliance rate across different priorities and categories?
* How effectively is the Level 1 team resolving issues at first contact (**FCR Proxy**)?

### Portugues (Brasil)
Este projeto e um portfolio end-to-end de engenharia e analise de dados, desenvolvido para simular uma operacao realista de IT Service Management (ITSM). Ele transforma eventos brutos de suporte tecnico em metricas de negocio acionaveis.

O objetivo e demonstrar competencia pratica em **processos ITIL/ITSM**, **modelagem dimensional de dados (Star Schema)** e **business intelligence**. Ao gerar um dataset realista com mais de 5.000 tickets de suporte e processa-lo por um pipeline completo de dados, este projeto responde perguntas operacionais criticas:
* Qual e a eficiencia operacional real (**Net MTTR**) ao isolar tempos de espera do usuario?
* Qual e a taxa real de conformidade com SLA entre diferentes prioridades e categorias?
* Quao efetivamente o time de Nivel 1 resolve incidentes no primeiro contato (**FCR Proxy**)?

## Architecture & Methodology | Arquitetura e Metodologia

### English
The core differentiator of this project is the use of the **Event Sourcing** paradigm for data generation and modeling.

Instead of merely generating a flat table of tickets, the Python pipeline acts as a state machine:
1. **`fact_ticket_event`**: Generates the exact chronological history of status transitions (e.g., *New -> In Progress -> Pending -> In Progress -> Resolved*).
2. **`fact_ticket`**: This final table is strictly derived from the event history.

This approach mirrors enterprise systems like ServiceNow or Jira and mathematically guarantees the integrity of complex KPIs, such as pausing the SLA clock while a ticket is awaiting user input.

### Portugues (Brasil)
O principal diferencial deste projeto e o uso do paradigma de **Event Sourcing** para geracao e modelagem de dados.

Em vez de gerar apenas uma tabela plana de tickets, o pipeline em Python funciona como uma maquina de estados:
1. **`fact_ticket_event`**: Gera o historico cronologico exato das transicoes de status (ex.: *New -> In Progress -> Pending -> In Progress -> Resolved*).
2. **`fact_ticket`**: Esta tabela final e derivada estritamente do historico de eventos.

Essa abordagem espelha sistemas corporativos como ServiceNow ou Jira e garante matematicamente a integridade de KPIs complexos, como pausar o relogio de SLA enquanto um ticket aguarda retorno do usuario.

## Tech Stack | Stack Tecnologica
* **Data Generation & Pipeline / Geracao de Dados e Pipeline:** Python (Pandas, Faker)
* **Storage & Data Warehouse / Armazenamento e Data Warehouse:** PostgreSQL (containerizado via Docker)
* **Transformations & KPIs / Transformacoes e KPIs:** SQL (CTEs, Window Functions, Aggregations)
* **Visualization / Visualizacao:** Power BI (dashboards executivos e operacionais)
* **Tactical Operations / Operacao Tatica:** Excel (Ops Pack para acompanhamento diario)

## Repository Structure | Estrutura do Repositorio
* `/case_study/`: Business-focused documentation detailing the problem, approach, and executive findings. / Documentacao orientada ao negocio com problema, abordagem e achados executivos.
* `/docs/`: Technical documentation including the Data Dictionary and Architecture. / Documentacao tecnica, incluindo Data Dictionary e Arquitetura.
* `/pipelines/`: Python scripts for generating the synthetic state-machine dataset and loading it into Postgres. / Scripts Python para gerar o dataset sintetico baseado em maquina de estados e carregar no Postgres.
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

### Portugues (Brasil)
Este projeto foi desenhado para ser 100% reproduzivel localmente usando Docker e Make.

1. **Clone o repositorio:**
   ```bash
   git clone https://github.com/andrewDDL/service-desk-performance-insights.git
   cd service-desk-performance-insights
   ```
2. **Prepare as variaveis de ambiente:**
   ```bash
   cp .env.example .env
   ```
3. **Execute as etapas de pipeline e analise:**
   *Os comandos detalhados serao documentados conforme os scripts de pipeline e modulos SQL forem adicionados.*