import asyncio
import os
from io import BytesIO
from aiohttp import ClientSession
from .mridecoder import mri_decoder


class AsyncLoader:
    def __init__(self, img_list, path='./somefiles', callback_func=None):
        self.__img_list = list(img_list)
        self.__imges_count = len(self.__img_list)
        self.__loaded_imges = [None for _ in range(self.__imges_count)]
        self.path = path
        self.__callback_func = callback_func
        try:
            os.makedirs(os.path.join(path, 'imges'))
        except FileExistsError:
            pass

    @property
    def indexes(self):
        return range(self.__imges_count)
    
    @property
    def status(self):
        loaded = self.__imges_count - self.__loaded_imges.count(None)
        return (loaded, self.__imges_count)

    async def wait(self):
        while None in self.__loaded_imges:
            await asyncio.sleep(0)
        return self

    async def load_by_index(self, index, session=None, status_info=False, reload=False):
        if not self.__loaded_imges[index] or reload:
            raw = await self.__load(index, session)
            filename = os.path.join(self.path,'imges',f'{index}.jpg')
            with open(filename, 'wb' ) as file:
                file.write( raw.getvalue())
            self.__loaded_imges[index] = filename

            await self.__make_callback()


    async def __load(self, index, session = None):
        link =  self.__img_list[index]
        raw = await self.__check_session(link, session)
        if '.mri' in str(link)[-4:]:
            raw = mri_decoder(raw)
        return raw

    async def __check_session(self, link, session = None):
        if not session:
            async with ClientSession() as session:
                raw = await self.__get_image_value(link, session)
        else:
            raw = await self.__get_image_value(link, session)
        return raw

    async def __get_image_value(self, link, session):
        while 1:
            try:
                tmp = str(link)
                async with session.get(tmp) as response:
                    if response.status ==200:
                        tmp_file = BytesIO()
                        part = await response.content.read(10**4)
                        while part:
                            tmp_file.write(part)
                            part = await response.content.read(10**4)
                        break
                    else:
                        print(response.status, tmp)
                        await asyncio.sleep(5)
            except Exception as ex:
                print(ex)
                await asyncio.sleep(5)

        return tmp_file

    async def __make_callback(self):
        if self.__callback_func:
            await self.__callback_func(self.status)
        else:
            await AsyncLoader.__std_callback_func(self.status)

    @classmethod
    async def __std_callback_func(self, status):
        done, all = status
        print('%0.2f' % (done/all*100) )
        await asyncio.sleep(0)
