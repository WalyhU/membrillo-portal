"""Broker SSE en memoria. Pub/Sub asyncio para notificar cambios de stock."""
import asyncio
import json
from typing import Set


class StockBroker:
    def __init__(self) -> None:
        self._subscribers: Set[asyncio.Queue] = set()
        self._lock = asyncio.Lock()

    async def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=100)
        async with self._lock:
            self._subscribers.add(q)
        return q

    async def unsubscribe(self, q: asyncio.Queue) -> None:
        async with self._lock:
            self._subscribers.discard(q)

    def publish(self, event: dict) -> None:
        """Sincrono: encola en cada cliente. Drop si la cola esta llena."""
        payload = json.dumps(event, default=str)
        for q in list(self._subscribers):
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                pass


broker = StockBroker()
