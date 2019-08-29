import time
import img2pdf
import aiohttp
from requests import get
from io import BytesIO
import PIL.Image as Image
import os
import threading
import asyncio
def print_progress(loader):
    fProgress = 100-100*loader.img_list.count(None)/loader.len_list
    print('%.2f ' % fProgress)
    
def mri_decoder(data):
    n = len(data) + 7
    header = [82, 73, 70, 70, 255 & n, n >> 8 & 255, n >> 16 & 255, n >> 24 & 255, 87, 69, 66, 80, 86, 80, 56]
    data = list(map(lambda x: x ^ 101, data))
    return bytes(header + data)
async def aget(url, session):
    async with session.get(url) as r:
        while True:
            if r.status == 200:
                f =  BytesIO()
                while True:
                    i = await r.content.read(10**4)
                    if not i: break
                    f.write(i)                  
                break
            else:
                print(400) 
                await asyncio.sleep(5)
    return f

def load_part(loader,tasks):
    while len(tasks)>0:
        time.sleep(1)
        try: 
            task = tasks.pop(0)
        except IndexError: 
            break
        while True:
            try:
                loader.load(task)
            except Exception as ex:
                print('['+str(task)+']'+f'{ex}')
                time.sleep(5)           
                continue
            break
        time.sleep(1)

class ImgListPDF:
    def __init__(self, link_list,path = './temp', callback_func = print_progress, args = () ):
        self.callback_func = callback_func
        self.args = (self,) + args
        self.link_list = link_list
        self.img_list = [None for i in link_list]
        self.len_list = len(self.link_list)
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
        else:
            os.makedirs(path)
        self.path = path

    async def aload(self, index, session, max_width = 1080):
        if index < - self.len_list or index > self.len_list:
            raise IndexError('index of image_link out the range')
        f = await aget(self.link_list[index], session)
        if '.mri' in self.link_list[index]:
            data = mri_decoder(f.getvalue())
            f = BytesIO()
            f.write(data)
        im = Image.open(f)
        im.thumbnail((max_width, max_width*5),  Image.ANTIALIAS)
        im.convert('RGB').save(f"{os.path.join(self.path,str(index))}.png" , "JPEG")
        print(f"{os.path.join(self.path,str(index))}.png")
        self.img_list[index] = f"{os.path.join(self.path,str(index))}.png"
        #if str(type(self.callback_func(*self.args)))== "<class 'coroutine'>":
        await self.callback_func(*self.args)

    async def aload_all(self):
        tasks = [i for i in range(len(self.img_list)) if not self.img_list[i]]
        async with aiohttp.ClientSession() as session:
            for task in tasks:
                await self.aload(task, session)

    def load(self,index, max_width = 1080):

        if index < - self.len_list or index > self.len_list:
            raise IndexError('index of image_link out the range')
        
        f =  BytesIO()
        while True: 
            r = get(self.link_list[index])      
            if r.ok:
                for i in r.iter_content(10**5):
                    f.write(i)
                break
            else:
                time.sleep(5)
                print(f'[{index}] {r}')
                continue
        im = Image.open(f)
        im.thumbnail((max_width, max_width*5),  Image.ANTIALIAS)
        im.convert('RGB').save(f"{os.path.join(self.path,str(index))}.png" , "JPEG")
        print(f"{os.path.join(self.path,str(index))}.png")
        self.img_list[index] = f"{os.path.join(self.path,str(index))}.png"
        self.callback_func(*self.args)
 
    @property
    def pdfbyte(self):
        if not None in self.img_list:
            self.bytes = img2pdf.convert(self.img_list)
            return self.bytes
        else:
            return 

    def load_in_threads(self, thread_count = 20):
        self.THREAD_COUNT = thread_count
        tasks = [i for i in range(len(self.img_list)) if not self.img_list[i]]
        self.task_list = [tasks[i*thread_count:(( (i+1)*500) if (i+1)*500< len(tasks) else None)] for i in range(len(tasks)//500+1) if i*500 != len(tasks)]
        for tasks in self.task_list:
            
            self.t_list = []
            for i in range(self.THREAD_COUNT):
                t = threading.Thread(target = load_part, args =(self,tasks))
                t.start()
                self.t_list.append(t)
            
    

    def load_all(self):
        while not self.pdfbyte:
            self.load(self.img_list.index(None))
        return self.pdfbyte
