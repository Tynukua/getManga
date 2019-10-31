import re
import json
from base64 import b64decode
from random import randint as ran
from bs4 import BeautifulSoup
import requests
import aiohttp

win_info = re.compile(r'''window.__info = (.+)''')

class MangaLibBaseApi:
    def __init__(self, url = 'https://mangalib.me/'):
        self._url = url

    async def aget_info(self, id):
        async with aiohttp.ClientSession() as session:
            async with session.get(self._url + 'manga-short-info',
                params = {'id', id} ) as r:
                api_request = await r.json()
        if 'slug' in api_request:
            return api_request

    async def aget_bs4(self, slug):
        async with aiohttp.ClientSession() as session:
            async with session.get(self._url + slug) as r:
                text = await r.text()
        return BeautifulSoup(text, features="lxml")
    
    def parse_window(self, html):
        for tag in html.select('script'):
            if 'window.__info ' in str(tag):
                return json.loads(win_info.search(tag.get_text()).group())

api = MangaLibBaseApi()

class MangaLibBook:
    def __init__(self, title):
        self.lang = 'RUS'
        self.title = title
        self.slug = None

    async def parse(self):
        if self.title: 
            self.__api_request = await api.aget_info(self.title)
            self.html = await api.aget_bs4(self.__api_request['slug'])
        else: 
            self.html = await api.aget_bs4(self.slug)
            self.title = self.html.select_one(
                    'div[data-post-id]').attrs['data-post-id']
            self.__api_request = await api.aget_info(self.title)
        self.__parse()
        return self

    def __parse(self):
        self.cover = self.html.select_one('img.manga__cover').attrs['src']
        
        chapter_list_tags = self.html.select('div[class="chapter-item"]')
        chapter_list = []
        for chapter in chapter_list_tags:
            chapter_tag = chapter.select_one('a')
            vol, chapter = re.search(r'/v([\d\.]+)/c([\d\.]+)', 
                chapter_tag.attrs['href']).groups()
            name = ' '.join(chapter_tag.get_text().split() )
            chapter_list.append((vol, chapter,name))
        chapter_list.reverse()
        self.chapter_list = chapter_list

        chapter_dict = {}
        for vol, chapter, name in self.chapter_list:
            if vol in chapter_dict:
                chapter_dict[vol].update({chapter:name})
            else:
                chapter_dict.update({vol:{chapter:name}})
        self.chapter_dict = chapter_dict
        
        self.name =  self.html.select_one(
            'meta[itemprop="name"]').attrs['content']
    
        self.description =  self.html.select_one(
            'meta[itemprop="description"]').attrs['content']

        link = self.html.select_one(
            'div[class="chapter-item"]').select_one('a').attrs['href']
        self.last_vol, self.last_chapter = re.search(r'/v([\d\.]+)/c([\d\.]+)',
            link).groups()
    
        rating = self.html.select_one(
            'div[class="manga-rating__value"]').get_text()
        rating = float(rating)
        self.rating = rating

        for i in self.html.select('div.info-list__row'): 
            if 'author' in str(i): 
                author = i.select_one('a').get_text()
                break
            author = None
        self.author = author 

        for i in self.html.select('div.info-list__row'): 
            if 'artist' in str(i): 
                artist = i.select_one('a').get_text()
                break
            artist = None
        self.artist =  artist 
        print(f'book {self.title}')
    
    @classmethod
    def by_link(self, link):
        title = re.search(r'mangalib.me/([0-z\-]*)', link).group(1)
        return MangaLibBook(title)
    
    @classmethod
    def by_slug(self, slug):
        self = MangaLibBook.__new__()
        self.slug = slug 
        self.title = None
        return self

    def get_volume(self, vol):
        return MangaLibVol(self.slug, vol, self)
        
    def get_chapter(self,vol, chapter):
        return MangaLibChapter(self.slug, vol, chapter)

    @property
    def img_list(self):
        img_list = []
        vol_list = list(self.chapter_dict.keys())
        
        for vol in vol_list:
            vol = MangaLibVol(self.title, vol, self)
            img_list+= vol.img_list
        
        return img_list

class MangaLibVol:
    def __init__(self, title, vol, manga = None):
        #print(f'v {title} {vol}')
        self.manga = MangaLibBook(title) if not manga else manga
        self.vol = vol
        self.title = title
        
    @property   
    async def img_list(self):
        self.chapter_list_for_vol = list(
            self.manga.chapter_dict.get(self.vol).keys() )
        #self.chapter_list_for_vol.reverse()
        del self.manga
        tmp_list = []
        for chapter in self.chapter_list_for_vol:
            chapter = MangaLibChapter(self.title, self.vol, chapter)
            tmp_list+= await chapter.img_list
        return tmp_list
    
 
class MangaLibChapter:
    def __init__(self, title, vol, chapter):
        #print(f'ch {title} {vol} {chapter}')
        self.chapter_url = f'https://mangalib.me/{title}/v{vol}/c{chapter}'
        self.path = None
        self._html = None

    @property
    async def img_list(self):
        if not self._html:
            self._html = await api.aget_bs4(self.chapter_url)
        if not self.path:
            self.path = api.parse_window(self._html).get('imgUrl')
        base_code = str(self._html.select_one('span.pp'))
        base_code = re.search(r'<span class="pp"><!-- ([\S\d=]*) -->',
            base_code).group(1)
        img_list = json.loads( b64decode(base_code))
        return [f'https://img{ran(1,3)}.mangalib.me{self.path}'+i.get('u') 
            for i in img_list]

