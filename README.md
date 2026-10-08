# Solana meme-coin intelligence

Decision-support platform. Paper mode only. No private keys and no live order routing.

This build exercises a labelled synthetic path:

`NO BUY` (identity unresolved) → `BUY SMALL NOW` → paper fill → `HOLD` → `EXIT`

Live Solana, Pump, Telegram, X, and OpenAI calls were not verified. See `docs/capability_matrix.md` and `docs/implementation_ledger.md`.

## Run

```bash
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py run_synthetic_scenario
python manage.py runserver 0.0.0.0:8000
python manage.py test tests
```

If SQLite on the project disk returns `disk I/O error`, set `SQLITE_PATH=/tmp/solana.sqlite3`.

Interface updates are page reloads and `GET /api/decisions/`. That is polling, not a stream.
