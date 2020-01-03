import asyncio
import os
from aiohttp import ClientSession
import aiofiles


class AsyncLoader:
    def __init__(self, img_list, path='./somefiles', callback_func=None, pool= None):
        self.__img_list = list(img_list)
        self.__imges_count = len(self.__img_list)
        self.__loaded_imges = [None for _ in range(self.__imges_count)]
        self.path = path
        self.__callback_func = callback_func
        try:
            os.makedirs(os.path.join(path, 'imges'))
        except FileExistsError:
            pass
        self.__pool = pool

    @property
    def indexes(self):
        return range(self.__imges_count)
    
    @property
    def status(self):
        loaded = self.__imges_count - self.__loaded_imges.count(None)
        return (loaded, self.__imges_count)

    def get_imges_paths(self):
        if not None in self.__loaded_imges:
            return self.__loaded_imges
            
    async def wait(self):
        while None in self.__loaded_imges:
            await asyncio.sleep(1)
        return self

    async def load_by_index(self, index, session=None, status_info=False, reload=False):
        if not self.__loaded_imges[index] or reload:
            self.__loaded_imges[index] = await self.__load(index, session)
            await self.__make_callback()

    async def __load(self, index, session = None):
        if not session:
            async with ClientSession() as session:
                filename = await self.__get_image_filename(index, session)
        else:
            filename = await self.__get_image_filename(index, session)
        return filename

    async def __get_image_filename(self, index, session):
        link = str(self.__img_list[index])
        format = link.rsplit('/', 1)[-1].rsplit('.', 1)[-1].split('?')[0]
        #                       ^                ^                  ^
        #           last part of path |   type of of file  | delete params from link
        filename = os.path.join(self.path,'imges',f'{index}.{format}')
        while 1:
            try:
                async with session.get(link) as response:
                    if response.status ==200:
                        async with aiofiles.open(filename) as file:
                            part = await response.content.read(10240)
                            while part:
                                await file.write(part)
                                part = await response.content.read(10240)
                            break
                    else:
                        print(response.status, link)
                        await asyncio.sleep(5)
                        link = str(self.__img_list[index])
            except Exception as ex:
                print(ex)
                await asyncio.sleep(5)
        return filename

    async def __make_callback(self):
        if self.__callback_func:
            await self.__callback_func(self.status)
        else:
            await AsyncLoader.__std_callback_func(self.status)

    @classmethod
    async def __std_callback_func(cls, status):
        done, all = status
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, print, ('\rLoading: %0.2f' % (done/all*100) ) )
        await asyncio.sleep(0)
