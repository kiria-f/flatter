import asyncio

from loguru import logger
from pynput.keyboard import Key, KeyCode, Listener

AnyKey = Key | KeyCode


class InputProcessor:
    def __init__(self):
        self._loop = asyncio.get_event_loop()
        self._queue = asyncio.Queue()
        self._listener = None

    def _on_press(self, key):
        if key is None:
            logger.warning('Key is None')
            return
        self._loop.call_soon_threadsafe(self._queue.put_nowait, key)

    async def read_key(self) -> AnyKey:
        return await self._queue.get()

    async def __aenter__(self):
        self._listener = Listener(on_press=self._on_press)
        self._listener.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._listener.stop()
        self._listener.join()
