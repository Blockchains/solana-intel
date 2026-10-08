# Implementation ledger

Exercised on 2026-10-08 in this environment (Python 3.10, no Docker, no Postgres, no Redis).

| Component | Implemented | Tested | Live verified | Blocker | Next step |
| --- | --- | --- | --- | --- | --- |
| Django project, models, migrations | yes | migrate on /tmp SQLite | n/a | artifacts volume SQLite I/O error | Postgres via Compose |
| Event envelope | yes | scenario write | no | no live source | wire a real collector |
| Synthetic vertical slice | yes | command printed the action path | synthetic only | none | keep labelled |
| Candle builder | yes | unit test late trade and empty bucket | no | no trade tape | connect Dex or RPC trades |
| Decision policy v1 | yes | 11 unit tests OK | no | thresholds provisional | walk-forward before any claim |
| Attention independence | yes | unit test | no | no X/Telegram | authorised ingestion |
| Token resolution | yes | contested unit test; scenario leader change | no | fixture scores | score from evidence |
| Paper accounting | yes | unit test and scenario realised pnl | no | no route quotes | quote adapter |
| Hot Takes | yes | one row stored | no | no scheduler | Celery beat |
| Positions | yes | open then closed paper | no | manual only | fill form |
| Dashboard + REST | yes | check passed; pages not browser-tested here | no | Tailwind via CDN | compile CSS |
| OpenAI adapter | fallback only | injection unit test | blocked | no key | schema call with budget |
| AIOHTTP client | wrapper only | not called | blocked | no credentialed source | one DexScreener read |
| Telegram | not called | no | blocked | bot token; chat membership | authorised chats only |
| X | not called | no | blocked | bearer and tier | recent search |
| Solana / Pump / Helius | documented | no | blocked | keys; Pump has no official public tape | PumpPortal or Helius, labelled |
| Celery / Redis | compose only | no | blocked | no Redis here | worker process |
| Selenium / Flask | omitted on purpose | n/a | n/a | not justified | do not add |
| Replay leakage corpus | filter in scenario and candle test | partial | no | no historical corpus | recorded tape |
| Real-money trading | not implemented | n/a | n/a | forbidden in this build | do not add keys |

Known defects:

- Artifacts filesystem returned SQLite `disk I/O error`. Use `SQLITE_PATH`.
- t+20 buy is only as good as fixture thresholds. Not a performance result.
- Caller sample size is not updated from outcomes.
- No coalesced reevaluation worker.
- Settings page requires login; other pages are read-only and unauthenticated.
- Docker Compose was not started.

Continuation prompt:

Implement a credentialed DexScreener poll adapter and a PumpPortal websocket collector behind OPERATING_MODE=live, refuse synthetic rows in that mode, and add a Celery beat task that reevaluates active Hot Takes. Do not add trading keys.
