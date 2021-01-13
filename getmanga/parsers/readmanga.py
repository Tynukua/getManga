import re, json
import asyncio
import io

from aiohttp import ClientSession
from scrapy import Selector
from ..loader import AsyncLoader
from .abcparser import ParserABC

mangaidregexp = re.compile(r'https:\/\/[rm][ei][an][dt]manga.live\/([^\/]+)')
scriptparser = re.compile('init\((.+)\)')



class ReadManga(ParserABC):
    @classmethod
    def urlparse(cls, url: str)->str:
        match =        mangaidregexp.search(url)
        if match:
            return match.group(1)

    async def parse_info(self):
        async with ClientSession as session:
            domain = self._manga._domain
            _id = self._manga._id
            async with session.get(f'https://{domain}/{_id}') as resp:
                if resp.status != 200:
                    raise ValueError(
                            f"https://{domain}/{_id} STATUS {resp.status}")
                self._page = await resp.text()
        
        selector = Selector(text=self._page)
        self._manga.title = selector.css('.name::text').get()
        self._manga.description = selector.css(
                'div.manga-description::text').get().strip()

        #parse authors:
        persons = selector.css('a.person-link::text').getall()
        translatos = selector.css(
                'span.elem_translator a.person-link::text').getall()
        for i in translatos: 
            persons.remove(i)
        self._manga.authors = persons
        self._manga

        # parse contents
        l = selector.xpath("//td[@class=' ']/a").xpath('@href').re(
                r'/vol(\d+)/(\d+)')
        self._manga.last_volume  = l[0]
        self._manga.last_chapter = l[1]
        while l:
            vol = l.pop(0)
            ch = l.pop(0)
            if not vol in self._manga.contents:
                self._manga.contents[vol] = []
            self._manga.contents[vol].append(ch)

    def __furl(self, vol, ch):
        return 'https://{domain}/{manga_id}/vol{vol}/{ch}?mtr=1'.format(
                domain = self._manga._domain,
                manga_id=self._manga.id,
                vol=vol,
                ch=ch
             )

    def __check(self, vol, ch):
        if vol is None: return 1
        elif vol in self._manga.contents:
            if ch is None or ch in self._manga.contents[vol]:
                return 1
        raise ValueError(f"No such volume or chapter {vol}-{ch}")           

    async def parse_images(self, vol = None, ch = None):
        self.__check(vol,ch) #TODO: check aioblocking
        async with ClientSession() as session:
            if not vol is None and not ch is None:
                async with session.get(self.__furl(vol,ch)) as resp:
                    text = await resp.text()
                return __parse_images(text)
            elif not vol is None and ch is None:
                urls=[self.__furl(vol,ch) for ch in self._manga.contents[vol]]
            elif vol is None and ch is None:
                urls = []
                for vol_i in self._manga.contents:
                    urls+=[self.__furl(vol_i,ch) for ch in self._manga.contents[vol_i]]
            al = AsyncLoader(min((len(urls), 20)),session=session)
            urls = [(u,io.StringIO()) for u in urls]
            al.put(urls)
            al.start()
            await al.wait()
            imgs = []
            loop = asyncio.get_running_loop()
            for _,ss in urls:
                sb = await loop.run_in_executor(None,ss.read,None)
                imgs += __parse_images(sb)
            return imgs

            
    
def __parse_images( text):
    selector = Selector(text= text)
    for script in selector.css('script').getall():
        if 'init' in script: break
    else:
        raise ValueError("Script not found")
    match = scriptparser.search(script)
    if not match:
        raise ValueError("Script not parsed")
    fargs = match.group(1)
    fargs = '[' + fargs.replace("'", '"') + ']'
    imgs_splited = json.loads(fargs)[0]
    imgs = [ ''.join(i[:3]) for i in imgs_splited]
    return imgs



