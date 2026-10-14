# DataPulse

Hybrid observability and business-event analytics platform. Learning project,
built collaboratively to prepare for a senior full-stack interview.

- Requirements: `docs/architecture/DataPulse_Technical_Project_Report_v1.pdf`
- Architecture: `docs/architecture/DataPulse_System_Architecture_Article.pdf`
- Build plan, concepts and interview bank: `docs/plan/DataPulse_Build_Plan.pdf`
- Current phase: **Phase 0 (foundation fixes)**. Update this line as phases complete.

## How we work together (read first)

- **Show before applying.** Claude writes the code, including core logic
  (models, validation, tenant scoping, Celery task idempotency,
  ClickHouse/Elasticsearch write paths). Before applying any change, show the
  code in chat, explain it, and wait for the user's OK. No silent edits, even
  small ones.
- **Explain as you go.** For each change: what it does, why, the trade-off or
  alternative, and how it could come up in an interview. Walk through core
  logic line by line.
- **Quiz at the end of each phase.** Ask 3–5 interview-style questions about
  what was built, and wait for the user's answers before giving feedback.
- Follow the phase order in the build plan; don't jump ahead.

## Commands

Infrastructure (from repo root):

```bash
docker compose up -d postgres redis   # minimum for the backend
docker compose up -d                  # + ClickHouse, Elasticsearch
docker compose ps
```

Backend (from `backend/`, venv at `backend/.venv`):

```bash
source .venv/bin/activate
python manage.py runserver
python manage.py migrate
celery -A config worker -l info
pytest                     # tests
ruff check . && ruff format .
```

## Architecture map

- `backend/config/`: settings (django-environ, reads `../.env`), URLs, Celery app
- `backend/apps/`: Django apps: `accounts`, `organizations`, `events`,
  `ingestion`, `processing` (Celery tasks), `audit`
- PostgreSQL: system of record (users, orgs, projects, ingestion jobs, audit)
- Redis: Celery broker only, never a source of truth
- ClickHouse: analytics; Elasticsearch: search. Both are eventually consistent.

## Conventions

- Thin views; business operations live in a service layer (`services.py`) so
  views, tasks and commands share them.
- Every queryset is scoped to the caller's projects. Never `Model.objects.all()`
  in a view. Other tenants' objects return 404, not 403.
- Celery tasks take IDs, not payloads; enqueue with `transaction.on_commit`;
  tasks must be idempotent (at-least-once delivery).
- ClickHouse/Elasticsearch queries are built server-side with a mandatory
  `project_id` filter and bound parameters, never string formatting.
- Python 3.12+, ruff (line length 100). API under `/api/v1/`.

## Gotchas

- Django runs on the **host**; Postgres is published on **5436** and Redis on
  **6380** (a separate Redis runs natively on this Mac on 6379, so don't use it).
  `.env` must use `localhost`, not Docker service names.
- `.env` is gitignored; `.env.example` is the template. Never commit secrets.
- The project folder path contains a space ("GOLANG PROJECTS"), so quote paths in
  shell commands.
