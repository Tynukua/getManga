import re
from .parsers import CLASS_DICT
    
class Manga:
    def __init__(self, link):
        if re.search(r'(\w+\.\w+)/?', link):
                site = re.search(r'(\w+\.\w+)/?', link).group(1)
                if not site in CLASS_DICT: 
                    raise UnknownWebsite(f"Don\'t support this website '{site}'")
                self.__link = link
                self.__site = site
                self.__title = None
        else: 
            raise UnknownWebsite(f'Can\'t find a domen name in {link}')


    async def parse(self):
        if self.__site and self.__title:
            manga = CLASS_DICT.get(self.__site)(self.__title)
            self.__manga = await manga.parse()
        elif self.__link:
            manga = CLASS_DICT.get(self.__site).by_link(self.__link)
            self.__manga = await manga.parse()
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
        
        self.__dict__.update( self.info)
        self.chapter_list = self.__manga.chapter_list
        self.chapter_dict = self.__manga.chapter_dict
        self.date_dict = self.__manga.date_dict
        return self

    @property
    async def img_list(self):
        return await self.__manga.img_list


    def get_volume(self, vol):
        vol = str(vol)
        if vol in self.__manga.chapter_dict:
            return self.__manga.get_volume(vol)
        return


    def get_chapter(self, chapter_num):
        chapter_num = str(chapter_num)
        for vol,chapter,name in self.__manga.chapter_list:
            if chapter == chapter_num:
                print(vol,chapter,name)
                chapter =  self.__manga.get_chapter(vol, chapter_num)
                chapter.name = name
                return chapter
        return

    @classmethod
    def get(cls, site, title):
        if not site in CLASS_DICT:
            raise UnknownWebsite(f"Don\'t support this website '{site}'")
        self = cls.__new__(cls)
        self.__link = None
        self.__site = site
        self.__title = title
        return self

class UnknownWebsite(ValueError):
    def __init__(self, text): pass
