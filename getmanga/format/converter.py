import asyncio
from PIL import Image
import aiofiles

def mri_decoder(data):
    n = len(data) + 7
    header = [82, 73, 70, 70, 255 & n, 
            n >> 8 & 255, n >> 16 & 255, 
            n >> 24 & 255, 87, 69, 66, 80, 
            86, 80, 56]
    data = list(map(lambda x: x ^ 101, data))
    return bytes(header + data)

FORMAT_HANDLERS = {
    'mri':mri_decoder
}

class Converter:
    def __init__(self, path_list, pool = None, callback = None):
        self.path_list = path_list
        self.__file_count = len(self.path_list)
        self.__converted_list = [None for i in range(self.__file_count)]
        self.__pool = pool
        self.__converted = 0
        self.__callback = callback if callback else Converter.__std_callback_func

    @property
    def status(self):
        return (self.__converted , self.__file_count)

    async  def convert_file(self, index):
        filename = self.path_list[index]
        format = filename.rsplit('.',1)[-1] 
        func = FORMAT_HANDLERS.get(format)
        if func:
            async with aiofiles.open(filename, 'rb') as f:
                data = await f.read()
            data = func(data)
            async with aiofiles.open(filename, 'wb') as f:
                f.write(data)
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            self.__pool, self.__convert_file, filename)
        self.__converted += 1
        await self.__callback(self.status)   

    def __convert_file(self, file):
        im = Image.open(file)
        im.convert("RGB")
        im.save(file, "JPEG")

    @classmethod
    async def __std_callback_func(cls, status):
        done, all = status
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, print, ('\rConverting %0.2f%% ...' % (done/all*100) ) )
        await asyncio.sleep(0)

