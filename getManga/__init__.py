from .parsers import *
import re
from . import exceptions
from .pdfer import ImgListPDF

CLASS_DICT = {
    'mangalib.me': mangalib.MangaLibBook,
    'mangarock.com':mangarock.MangaRockBook}


class Manga:
    def __init__(self, link = None, site = None, title = None):
        if not site and not title:
            if re.search(r'(\w+\.\w+)/?', link):
                site = re.search(r'(\w+\.\w+)/?', link).group(1)
                if not site in CLASS_DICT: 
                    raise Exception(f"Don\'t support this website '{site}'")
                self.__manga = CLASS_DICT.get(site).by_link(link)
            else: 
                raise Exception('Can\'t find a domen name in {link}')
        else:
            if not site in CLASS_DICT: 
                raise Exception(f"Don\'t support this website '{site}'")
            self.__manga = CLASS_DICT.get(site)(title)
        self.site = site
        #self.manga = self.__manga
        
        self.info = {
            'title' : self.__manga.title,
            'name':self.__manga.name,
            'cover': self.__manga.cover,
            'description': self.__manga.description,
            'lang': self.__manga.lang,
            'rating':self.__manga.rating,
            'last_chapter':  self.__manga.last_chapter,
            'last_volume': self.__manga.last_vol,
            'author':self.__manga.author,
            'artist': self.__manga.artist}

        self.title = self.__manga.title
        self.name = self.__manga.name
        self.cover = self.__manga.cover
        self.description = self.__manga.description
        self.lang = self.__manga.lang
        self.rating = self.__manga.rating
        self.last_chapter = self.__manga.last_chapter
        self.last_volume = self.__manga.last_vol
        self.author = self.__manga.author
        self.artist = self.__manga.artist
        self.chapter_list = self.__manga.chapter_list
        self.chapter_dict = self.__manga.chapter_dict

    @property
    def img_list(self):
        return self.__manga.img_list


    def get_volume(self, vol):
        vol = str(vol)
        if vol in self.__manga.chapter_dict:
            return self.__manga.get_volume(vol)
        return


    def get_chapter(self, chapter_num):
        chapter_num = str(chapter_num)
        for vol,chapter,name in self.__manga.chapter_list:
            if chapter == chapter_num:
                chapter =  self.__manga.get_chapter(vol, chapter_num)
                chapter.name = name
                return chapter
        return

    @classmethod
    def get(self, site, title):
        return Manga(None,site,title)