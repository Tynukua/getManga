import asyncio
import os
import img2pdf
import aiofiles

class MangaToPDF:
    def __init__(self, filename_list, path='./something',bookname='book.pdf'):
        self.fl_list = filename_list
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        self.path = os.path.join(path, bookname)

    async def make_book(self):
        loop = asyncio.get_running_loop()
        self.data = await loop.run_in_executor(None, img2pdf.convert, self.fl_list)
        await self.__write()
        return self.path

    def __write(self):
        async with aiofiles.open(self.path, 'wb') as f:
            await f.write(self.data) 
        del self.data      
