# 🎓 School Master API

<p align="center">
  <b>Enterprise School Management System</b><br>
  <i>Uma API robusta simulando um ambiente real de startup, focada em segurança, escalabilidade e processos ágeis.</i> 🚀
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Fase_1_(MVP_Seguro)-green?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/Coverage->80%25-blue?style=for-the-badge" alt="Coverage">
</p>

---

## 📑 Visão de Produto e Metodologia

Diferente de projetos comuns, o **School Master** foi desenvolvido simulando o ciclo de vida real de um produto de software:

1. **CEO/Stakeholder (IA):** Definiu 8 pilares estratégicos de negócio, como combate à evasão escolar e gestão financeira.
2. **Product Owner (IA):** Traduziu os desejos de negócio em um **Backlog Técnico Sênior** com User Stories (US), Critérios de Aceite e priorização P0/P1/P2.
3. **Desenvolvedor (Enrico):** Implementa as funcionalidades focando em Design Patterns e infraestrutura resiliente.

> 🔗 **[Clique aqui para visualizar o Board do Projeto (Roadmap/Kanban)]**
> *[text](https://github.com/users/enricoferrer/projects/1)*

---

## ✨ Diferenciais Técnicos (Enterprise-Grade)

* 🔐 **Segurança P0:** Autenticação JWT com *Refresh Token Rotation* e RBAC (Controle de acesso granular)
* 🛡️ **Audit Log:** Middleware de auditoria imutável para rastreabilidade total de operações (Quem? Quando? O quê?)
* 📊 **Analytics & Reports:** Processamento de dados de frequência e desempenho com geração de PDFs e Excel
* ⚙️ **Processamento Assíncrono:** Uso de **Celery + RabbitMQ** para tarefas pesadas
* 🚀 **Performance:** Cache distribuído com **Redis**

---

## 🧱 Arquitetura e Design Patterns

```
app/
├── core/          # Configurações globais, Segurança e Auditoria
├── models/        # Modelos SQLAlchemy (Event Sourcing para Logs)
├── schemas/       # DTOs de validação (Pydantic)
├── services/      # Regras de Negócio e Patterns (Strategy, Factory)
├── routes/        # Controllers/Endpoints versionados (v1)
└── main.py        # Configuração da aplicação FastAPI
```

---

## 🚀 Tecnologias e Stack

* **Backend:** Python / FastAPI
* **Banco de Dados:** PostgreSQL (Relacional) / Redis (Cache)
* **Mensageria/Filas:** RabbitMQ / Celery
* **DevOps:** Docker / Docker Compose / GitHub Actions (CI/CD)
* **Testes:** Pytest (Cobertura de 80%+)

---

## 🗺️ Roadmap de Desenvolvimento

### Fase 1: MVP Seguro (Em andamento 🚧)

* [ ] US-001: Autenticação JWT & Refresh Tokens
* [ ] US-002: RBAC (Permissões de Admin, Professor, etc)
* [ ] US-003: Sistema de Auditoria de Dados
* [ ] TD-001: Rate Limiting & Proteção Anti-Abuso

### Fase 2: Gestão & Monetização

* [ ] US-004: Analytics de Frequência e Evasão
* [ ] US-005: Gestão Financeira (PIX/NFe)
* [ ] US-006: Notas e Cálculo Automático de Médias

---

## 👨‍💻 Autor

**Enrico Ferrer**
Desenvolvedor Fullstack focado em Python/Java 🚀
