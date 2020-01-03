import asyncio
import os
import img2pdf
import aiofiles

class MangaToPDF:
    def __init__(self, filename_list, path='./something',bookname='book.pdf', pool= None):
        self.fl_list = filename_list
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        self.path = os.path.join(path, bookname)
        self.pool = pool
        
    async def make_book(self):
        loop = asyncio.get_running_loop()
        self.data = await loop.run_in_executor(self.pool, img2pdf.convert, self.fl_list)
        await self.__write()
        return self.path

    async def __write(self):
        async with aiofiles.open(self.path, 'wb') as f:
            await f.write(self.data) 
        del self.data      
