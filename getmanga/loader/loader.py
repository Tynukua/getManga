import asyncio
from typing import Tuple
from queue import Queue
import io

from aiohttp import ClientSession
from aiofiles.base import AsyncBase

PAIR_URL_BUFER = Tuple[str,io.IOBase]

class AsyncLoader:
    def __init__(self, worker_count = 20, session: ClientSession = None):
        self._wc = worker_count
        self.__worker_status = [0 for _ in range(self._wc)]
        self.queue: Queue = Queue()
        self.session = session 
        self.__working = False
        if self.session is None:
            self.session = ClientSession()

    async def __get(self, pair: PAIR_URL_BUFER):
        resp = await self.session.get(pair[0])
        if resp.status != 200:
            if len(url) >100:
                url = url[:100] + '...'
            raise ValueError(f"[{resp.status}] GET {url}")
        stream = pair[1]
        if isinstance(stream, io.TextIOBase):
            part = await resp.text()
        if isinstance(stream, AsyncBase):
            await stream.write(part)
        else:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None,stream.write,part)
        resp.close()

    def put(self,items: list):
        for i in items:
            self.queue.put(i)

    def start(self):
        self.__working = True
        for i in range(self._wc):
            asyncio.create_task(self.__worker(i))

    async  def wait(self):
        while not self.queue.empty() or 1 in self.__worker_status:
            await asyncio.sleep(3)

    async def __worker(self, worker_id):
        self.__worker_status[worker_id] = 1
        while  self.__working:
            if self.queue.empty():
                self.__worker_status[worker_id] = 0
                await asyncio.sleep(2)
                continue
            self.__worker_status[worker_id] = 1
            url = self.queue.get()
            await self.__get(url)


