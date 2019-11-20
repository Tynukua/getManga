import json
from datetime import datetime
from requests import get
import re
import aiohttp


API_URL = 'https://api.mangarockhd.com/query/web401/'

class MangaRockException(Exception):
    pass

class MangaRockAPI:
    def __init__(self, url):
        self.url = url

    def __data_return(self, r_json):
        if not r_json['code']:
            return r_json['data']
        else:
            raise MangaRockException("MangaRock wrong request")   

    async def aget_info(self, oid):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url+'info', params = {'oid' : oid}) as request:
                return self.__data_return( await request.json()) 
        
    async def aget_pages(self, oid):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url+'pages', params = {'oid' : oid}) as request:
                return self.__data_return( await request.json()) 
            
api = MangaRockAPI(API_URL)


class MangaRockBook:
    def __init__(self, title):
        self.title = title
        self.book_url = 'https://mangarock.com/manga/' + title #ненужная хуета на самом деле
        self.lang = 'ENG'
        self.last_vol = 'Unknown'


    async def parse(self):
        self.__api_request = await api.aget_info(self.title)
        self.__parse()
        return self
    
    def __parse(self):
        self.name = self.__api_request.get('name')
        self.description = self.__api_request.get('description')
        self.cover = self.__api_request.get('cover')
        self.last_vol = 'Unknown'
        self._chapters = self.__api_request.get('chapters')
        self.last_chapter = self._chapters[-1]['name']
        self.date_dict = {}
        self.chapter_list = []
        for i in range(len(self._chapters)):
            part = str(i//5+1)
            oid = str(i)
            name = self._chapters[i].get('name')
            self.chapter_list.append((part, oid, name))
            self.date_dict.update({oid:
                datetime.fromtimestamp(
                    self._chapters[i].get('updatedAt') )})
        
        self.chapter_dict = {}
        for part, oid, name in self.chapter_list:
            if part in self.chapter_dict:
                self.chapter_dict[part].update({oid:name})
            else:
                self.chapter_dict.update({part:{oid:name}})
        self.author, self.artist = None, None
        for creator in self.__api_request.get('authors'):
            if creator.get('role') == 'author':
                self.author = creator.get('name')
            elif creator.get('role') == 'artist':
                self.artist = creator.get('name')

            elif self.author and self.artist:
                break
            else:
                break

        rating = self.__api_request.get('categories')
        mark = 0
        for i in range(len(rating)):
            mark += rating[i]*(i+1)
            
        self.rating = mark/sum(rating)
        
    def get_volume(self, vol):
        if vol in self.chapter_dict: 
            return MangaRockVol(self, vol)
        
    def get_chapter(self, vol, chapter_num):
        if int(chapter_num) in range(len(self._chapters)):
            return MangaRockChapter(self, chapter_num)
                
    @classmethod
    def by_link(self, link):
        title = re.search(r'mangarock\.com/manga/([a-z\-A-Z0-9]+)/?', link).group(1)
        return MangaRockBook(title)

class MangaRockVol:
    def __init__(self, manga, vol):
        self.vol = str(vol)
        self.chapter_dict = manga.chapter_dict.get(self.vol)
        if not self.chapter_dict:
            raise MangaRockException('Volume not found')
        self.chapter_list = [i[1] for i in manga.chapter_list if i[0] == self.vol]
        self.date = max([manga.date_dict.get(str(i)) for i in self.chapter_list])
        self.manga = manga

    @property
    async def img_list(self):
        img_list = []
        for _, oid, _ in self.chapter_list:
            chapter = MangaRockChapter(self.manga, oid)
            img_list += await chapter.img_list
        return img_list


class MangaRockChapter:
    def __init__(self, manga, chapter):
        if int(chapter) in range(len(manga._chapters)):
            self.__chapter = manga._chapters[int(chapter)]
            self.name = self.__chapter.get('name')
            self.oid = self.__chapter.get('oid')
            self.date = manga.date_dict.get(str(chapter))
        else:
            raise MangaRockException('Unknown chapter')

    @property
    async def img_list(self):
        return await api.aget_pages(self.oid)
