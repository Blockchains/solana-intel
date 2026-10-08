# API

`GET /api/decisions/` returns the latest stored decisions. Poll it. It is not a stream.

`GET /api/health/` returns source verification labels and hot-take count.

Anonymous throttle is 60/minute. Write endpoints are not exposed. There is no trading endpoint.
