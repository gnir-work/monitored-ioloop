import random

from httpx import AsyncClient
from httpx import Limits, Timeout
import asyncio

URLS = [
    "http://localhost:1441/ping",
    "http://localhost:1441/async_slow?sleep_for=5&coroutines_number=10",
    "http://localhost:1441/blocking_slow?sleep_for=1",
]


async def main() -> None:
    async with AsyncClient(
        limits=Limits(max_connections=20), timeout=Timeout(timeout=30)
    ) as client:
        await asyncio.gather(*[client.get(random.choice(URLS)) for _ in range(10)])


if __name__ == "__main__":
    asyncio.run(main())
