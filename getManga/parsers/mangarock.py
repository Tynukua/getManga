import json
from requests import get
import re


API_URL = 'https://api.mangarockhd.com/query/web401/'

class MangaRockException(Exception):
    pass
class MangaRockAPI:
    def __init__(self, url):
        self.url = url
            
    
    def get_info(self, oid):
        r = get(self.url+'info', params = {'oid' : oid})
        r_json = r.json()
        if not r_json['code']:
            return r_json['data']
        else:
            print(f"Wrong request: info '{oid}'")
            return


    def get_pages(self, oid):
        r = get(self.url+'pages', params = {'oid' : oid})
        r_json = r.json()
        if not r_json['code']:
            return r_json['data']
        else:
            print(f"Wrong request: pages '{oid}'")
            return

api = MangaRockAPI(API_URL)


class MangaRockBook:
    def __init__(self, title):
        self.__api_request = api.get_info(title)
        self.title = title
        self.book_url = 'https://mangarock.com/manga/' + title #ненужная хуета на самом деле
        self.lang = 'ENG'
        self.name = self.__api_request.get('name')
        self.description = self.__api_request.get('description')
        self.cover = self.__api_request.get('cover')
        self.last_vol = 'Unknown'
        self._chapters = self.__api_request.get('chapters')
        self.last_chapter = self._chapters[-1]['name']

        self.chapter_list = []
        for i in range(len(self._chapters)):
            part = str(i//5+1)
            oid = str(i)
            name = self._chapters[i].get('name')
            self.chapter_list.append((part, oid, name))
        
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
        self.chapter_list = [i for i in manga.chapter_list if i[0] == self.vol]
        self.manga = manga

    @property 
    def img_list(self):
        img_list = []
        for _, oid, _ in self.chapter_list:
            chapter = MangaRockChapter(self.manga, oid)
            img_list += chapter.img_list
        return img_list
              

class MangaRockChapter:
    def __init__(self, manga, chapter):
        if int(chapter) in range(len(manga._chapters)):
            self.__chapter = manga._chapters[int(chapter)]
            self.name = self.__chapter.get('name')
            self.oid = self.__chapter.get('oid')
        else:
            raise MangaRockException('Unknown chapter')


    @property
    def img_list(self):
        return api.get_pages(self.oid)
