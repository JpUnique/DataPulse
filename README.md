# DataPulse

DataPulse is a hybrid observability and business-event analytics platform for
ingesting, processing, searching, and analyzing application telemetry and
business events.

> **Status: early scaffolding (Milestone 1–2).** The Django project, Celery
> wiring, and local infrastructure exist. Ingestion, processing, analytics,
> search, and the frontend are not implemented yet. See
> [Roadmap](#roadmap).

## Architecture

![DataPulse system architecture](docs/architecture/DataPulse%20System%20Architecture%20Infographic.png)

Events are sent to a Django REST Framework ingestion API, which validates them,
records an ingestion job in PostgreSQL, and hands the work to Celery workers
through Redis. Workers write processed events to ClickHouse for analytics and
Elasticsearch for search. A Next.js frontend reads everything through the API.

| Component     | Responsibility                                                    |
| ------------- | ----------------------------------------------------------------- |
| Django + DRF  | Ingestion API, authentication, validation, job tracking           |
| Celery        | Background processing, retries, deduplication                     |
| Redis         | Celery broker; short-lived caching and rate limiting              |
| PostgreSQL    | System of record: users, organizations, projects, jobs, audit log |
| ClickHouse    | Analytical event store and time-series aggregation                |
| Elasticsearch | Full-text event search and structured filtering                   |
| Next.js       | Dashboards, event explorer, job status (planned)                  |
| Observability | Grafana stack and Sentry for metrics, logs, traces (planned)      |

Full design documents:

- [Technical Project Report](docs/architecture/DataPulse_Technical_Project_Report_v1.pdf): goals, requirements, event contract, acceptance criteria
- [System Architecture](docs/architecture/DataPulse_System_Architecture_Article.pdf): component responsibilities, consistency, failure handling

## Repository layout

```text
.
├── backend/              Django project (Python package: datapulse-backend)
│   ├── config/           settings, URLs, Celery app, WSGI/ASGI
│   ├── apps/             Django apps (processing, events, ingestion, ...)
│   ├── tests/
│   ├── manage.py
│   └── pyproject.toml
├── docs/architecture/    Design documents and diagrams
├── docker-compose.yml    Local infrastructure (Postgres, Redis, ClickHouse, Elasticsearch)
└── .env.example          Environment variable template
```

## Prerequisites

- Python 3.12+
- Docker Desktop (or Docker Engine with Compose v2)
- Git

## Getting started

The infrastructure runs in Docker and the Django app runs on your machine.

### 1. Configure the environment

```bash
cp .env.example .env
```

Then edit `.env` and set `DJANGO_SECRET_KEY`, `POSTGRES_PASSWORD` and
`CLICKHOUSE_PASSWORD`. The other values are already set for running Django on
your machine against the ports Docker publishes.

### 2. Start the infrastructure

```bash
# Minimum needed for the backend today
docker compose up -d postgres redis

# Or everything, including ClickHouse and Elasticsearch
docker compose up -d
```

Check status with `docker compose ps`. Every service should report `healthy`.

| Service       | Host port                  |
| ------------- | -------------------------- |
| PostgreSQL    | 5436                       |
| Redis         | 6380                       |
| ClickHouse    | 8123 (HTTP), 9000 (native) |
| Elasticsearch | 9200                       |

### 3. Install the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 4. Run the backend

```bash
python manage.py migrate
python manage.py runserver        # http://localhost:8000/admin/
```

In a second terminal, start a Celery worker:

```bash
cd backend && source .venv/bin/activate
celery -A config worker -l info
```

Check that the worker can run a task:

```bash
python manage.py shell -c \
  "from apps.processing.tasks import add_numbers; print(add_numbers.delay(2, 3).get(timeout=10))"
# 5
```

## Development

Run these from `backend/`:

```bash
pytest            # tests
ruff check .      # lint
ruff format .     # format
```

## Stopping and resetting

```bash
docker compose down        # stop containers, keep data
docker compose down -v     # stop containers and delete all volumes
```

## Roadmap

Milestones from the technical report:

1. Requirements: done (see report)
2. Architecture: in progress
3. Synthetic data generator and ingestion API
4. Celery processing, ClickHouse analytics, Elasticsearch indexing
5. Next.js frontend
6. Observability (Sentry, Grafana stack) and GitHub Actions CI
7. Million-event load and recovery testing
