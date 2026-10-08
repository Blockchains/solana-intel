# Runbook

## Synthetic

```bash
cd solana-intel
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py run_synthetic_scenario
python manage.py runserver 0.0.0.0:8000
```

Open `/`. API: `/api/decisions/` and `/api/health/`. Settings page requires an admin user: `python manage.py createsuperuser`.

## Tests

```bash
python manage.py test tests
```

## Production compose

Requires Docker. Not exercised here.

```bash
docker compose up --build
```

Set `OPERATING_MODE=live` only with real credentials. Live mode must not load the synthetic command output.

## Backup

SQLite: copy `db.sqlite3`. Postgres: `pg_dump`. Restore before restarting workers.

## What is not operational

Celery workers, Solana streams, Telegram, X, OpenAI live calls, real paper-trading exchange routes, and automatic execution.
