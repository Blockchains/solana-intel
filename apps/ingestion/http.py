"""AIOHTTP client wrapper. Live calls are optional and never silent-synthetic."""

import asyncio
import random


class HttpClient:
    def __init__(self, limit=4, timeout=15):
        self.limit = limit
        self.timeout = timeout

    async def get_json(self, url, headers=None):
        import aiohttp
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        connector = aiohttp.TCPConnector(limit=self.limit)
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            for attempt in range(3):
                try:
                    async with session.get(url, headers=headers or {}) as resp:
                        resp.raise_for_status()
                        return await resp.json()
                except Exception:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(0.2 * (2 ** attempt) + random.random() * 0.1)
