# Source capability matrix

Verified against public docs on 2026-10-08. None of these were live-called in this build.

| Provider | Docs | Auth | Subscription | Data | Stream | Poll | History | Limits | Timestamps | Restrictions | Status | Live verified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Solana JSON-RPC | solana.com/docs | provider key for Helius | Helius free 10 rps | accounts, tx, slots | websockets accountSubscribe, logsSubscribe | getTransaction | provider-dependent | Helius free 10 rps; getTransaction batch max 100 | blockTime is unix seconds, null if unavailable | public RPC is rate-limited and not a full archive | adapter not implemented beyond notes | blocked |
| Helius LaserStream | helius.dev/docs | API key | paid for mainnet stream | program activity | gRPC/WebSocket | n/a | replay on paid plans | plan-based | provider event time | key required | not implemented | blocked |
| Pump.fun first party | frontend-api-v3.pump.fun is a site API, not a published market-data contract | JWT on many routes | none public | site data | not a documented public stream | site routes | undocumented | undocumented | undocumented | do not scrape behind auth | not used | blocked |
| PumpPortal | pumpportal.fun/data-api/real-time | none stated for data socket | none stated | new token, trades, migration | wss://pumpportal.fun/api/data | no | live only | one socket; multi-connect can be timed out | provider event | third party, not Pump.fun | documented only | blocked |
| pumpapi.io | pumpapi.io/stream | none stated for stream | trade API is separate | multi-venue events | wss://stream.pumpapi.io/ | no | live | one connection | provider event | third party | not used | blocked |
| DexScreener | docs.dexscreener.com | none | none | pairs, token pools | no | yes | latest pairs, not full trade tape | 60-300 rpm by route | pair updated time | no guaranteed trade-level history | not exercised | blocked |
| Telegram Bot API 10.3 | core.telegram.org/bots/api | bot token | none | updates in chats the bot is in | long poll getUpdates or webhook | getUpdates | only unconfirmed updates, max 100 | 409 if webhook set; 429 retry_after | message.date unix | cannot read arbitrary channels or private groups | not exercised | blocked |
| X API | developer.x.com | bearer | paid tiers | authorised posts | filtered stream on eligible tiers | recent search | tier-limited | tier-limited | created_at | no arbitrary account coverage | not exercised | blocked |
| OpenAI | platform.openai.com | API key | billed | extraction only | no | chat completions | n/a | budget in env | response time | untrusted source text | fallback only | blocked |

No detected issue is not "safe". Missing credentials are blockers, not empty activity.
