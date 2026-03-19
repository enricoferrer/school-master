# 🎓 School Master API

<p align="center">
  <b>Uma API moderna para gerenciamento de dados escolares</b><br>
  Desenvolvida com foco em boas práticas, arquitetura limpa e performance 🚀
</p>

---

## ✨ Destaques do projeto

- ⚡ API rápida construída com **FastAPI**
- 🧠 Arquitetura organizada em camadas
- 🗄️ Integração com **PostgreSQL**
- 🐳 Pronta para produção com **Docker**
- 🔗 Relacionamentos reais entre entidades (1:N)
- 📦 Validação robusta com **Pydantic**

---

## 🧠 Sobre o projeto

O **School Master** é uma API REST desenvolvida como projeto de portfólio, simulando um sistema completo de gestão escolar.

Ela permite o gerenciamento de:

- 👤 Usuários
- 🎓 Alunos
- 🏫 Turmas
- 👨‍🏫 Funcionários
- 📚 Relacionamentos entre entidades

O objetivo do projeto é demonstrar domínio em:

- Construção de APIs escaláveis
- Organização de código backend
- Integração com banco de dados relacional
- Boas práticas de desenvolvimento

---

## 🧱 Arquitetura

```bash
app/
├── core/          # Configurações e conexão com banco
├── models/        # Modelos (SQLAlchemy)
├── schemas/       # Validação (Pydantic)
├── services/      # Regras de negócio
├── routes/        # Endpoints
└── main.py        # Entrada da aplicação
```

---

## 🚀 Tecnologias

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- Docker
- Docker Compose

---

## 🐳 Rodando com Docker (recomendado)

### Subir o projeto

```bash
docker-compose up --build
```

### Acessar a API

- 🔗 http://localhost:8000/docs
- 🔗 http://localhost:8000/redoc

### Parar containers

```bash
docker-compose down
```

---

## 🛠️ Rodando localmente (sem Docker)

### 1. Clone o repositório

```bash
git clone https://github.com/enricoferrer/school-master.git
cd school-master
```

### 2. Ambiente virtual

```bash
python -m venv venv
source venv/bin/activate
venv\Scripts\activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar banco

```env
DATABASE_URL=postgresql://user:password@localhost:5432/school_master
```

### 5. Rodar API

```bash
uvicorn app.main:app --reload
```

---

## 📡 Endpoints

A API possui documentação automática:

- Swagger UI → `/docs`
- Redoc → `/redoc`

---

## 📚 Conceitos aplicados

- Arquitetura em camadas
- Separação de responsabilidades
- ORM com SQLAlchemy
- Validação com Pydantic
- API RESTful

---

## 🚀 Próximos passos

- 🔐 Autenticação com JWT
- 👥 Sistema de permissões
- 📊 Relatórios
- 📈 Observabilidade (logs/metrics)

---

## 🤝 Contribuição

Contribuições são bem-vindas!

```bash
# fluxo padrão
fork -> branch -> commit -> pull request
```

---

## 📄 Licença

MIT

---

## 👨‍💻 Autor

**Enrico Ferrer**

<p align="center">
  Feito com 💻 e café ☕
</p>
