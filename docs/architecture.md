# Architecture

One Django application. Ingestion, features, and decisions are modules, not separate services.

PostgreSQL is the durable store in the Compose file. This environment has no Postgres or Redis, so the exercised path uses SQLite. Redis is the intended Celery broker and is not the historical store.

Operating modes:

- synthetic: labelled fixtures only
- replay: recorded rows with available_at <= clock
- live: configured sources only; no silent synthetic fallback

Actions are chosen only in apps/decisions/policy.py. The OpenAI adapter may extract entities. It cannot emit BUY SMALL NOW.

Interface updates are HTTP polls. There is no market WebSocket in this build.

Flask is omitted. A second web stack had no benefit. Selenium is omitted. Market data must not come from a browser.
