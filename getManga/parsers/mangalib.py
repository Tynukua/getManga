import re
import json
from base64 import b64decode
from random import randint as ran
from bs4 import BeautifulSoup
import requests

class MangaLibBook:
    def __init__(self, title):
        if title.isdigit():
            api_request =requests.get(
                f'https://mangalib.me/manga-short-info?id={title}')
            if 'slug' in api_request.json():
                self.title = title
                self.slug =  api_request.json()['slug']
                self.book_url = 'http://mangalib.me/' + self.slug 

                response = requests.get(self.book_url)
                if not response.ok:
                    raise Exception(f"Book '{title}' not exists") #MangaLibBookNotFound
                self.html = BeautifulSoup(response.text, features="lxml")
        else:  
            self.slug = title
            self.book_url = 'http://mangalib.me/' + title
            response = requests.get(self.book_url)
            if not response.ok:
                raise Exception(f"Book '{title}' not exists") #MangaLibBookNotFound
            else:
                self.html = BeautifulSoup(response.text, features="lxml")
                self.title = self.html.select_one(
                    'div[data-post-id]').attrs['data-post-id']
        self.lang = 'RUS'
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
        print(f'v {title} {vol}')
        self.manga = MangaLibBook(title) if not manga else manga
        self.vol = vol
        self.title = title
        
    @property   
    def img_list(self):
        self.chapter_list_for_vol = list(
            self.manga.chapter_dict.get(self.vol).keys() )
        #self.chapter_list_for_vol.reverse()
        del self.manga
        tmp_list = []
        for chapter in self.chapter_list_for_vol:
            chapter = MangaLibChapter(self.title, self.vol, chapter)
            tmp_list+= chapter.img_list
        return tmp_list
    
 
class MangaLibChapter:
    def __init__(self, title, vol, chapter):
        print(f'ch {title} {vol} {chapter}')
        self.chapter_url = f'https://mangalib.me/{title}/v{vol}/c{chapter}'
        self.path = f'mangalib.me/manga/{title}/chapters/{vol}-{chapter}'
        page = requests.get(self.chapter_url)
        if not page.ok:
            raise Exception(f"Chapter '{title}-{vol}-{chapter}' not exists") #MangaLibChapterNotFound
        self.html = BeautifulSoup(page.text, features="lxml")

    @property
    def img_list(self):
        #self.html = BeautifulSoup(download(self.chapter_url), features="lxml")
        base_code = str(self.html.select_one('span.pp'))
        base_code = re.search(r'<span class="pp"><!-- ([\S\d=]*) -->',
            base_code).group(1)
        img_list = json.loads( b64decode(base_code))
        return [f'https://img{ran(1,3)}.{self.path}/'+i.get('u') 
            for i in img_list]
        

