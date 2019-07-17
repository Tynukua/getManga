import requests
from bs4 import BeautifulSoup
import re
import json
from base64 import b64decode
from random import randint as ran

class MangaLibBook:
	def __init__(self, title):
		print(f'book {title}')
		self.title = title
		self.book_url = 'http://mangalib.me/'+ self.title
		response = requests.get(self.book_url)
		if not response.ok:
			raise Exception(f"Book '{title}' not exists")
		else:
		self.html = BeautifulSoup(response.text, features="lxml")

	@property
	def cover(self):
		return self.html.select_one('img.manga__cover').attrs['src']

	@property
	def chapter_list(self):
		chapter_list_tag = self.html.select('div[class="chapter-item"]')
		chapter_list = []
		for chapter in chapter_list_tag:
			link = chapter.select_one('a').attrs['href']
			vol, chapter = re.search('/v([\d\.]+)/c([\d\.]+)',link).groups()
			chapter_list.append((vol, chapter))
		return chapter_list
	
	@property
	def chapter_dict(self):
		chapter_dict = {}
		for key, value in self.chapter_list:
			if key in chapter_dict.keys():
				chapter_dict[key].append(value)
			else:
				chapter_dict.update({key:[value]})
		return chapter_dict
		
	@property
	def name(self):
		return self.html.select_one('meta[itemprop="name"]').attrs['content']
	
	@property
	def description(self):
		return self.html.select_one('meta[itemprop="description"]').attrs['content']

	@property
	def last_chapter(self):
		link = self.html.select_one('div[class="chapter-item"]').select_one('a').attrs['href']
		vol, chapter = re.search('/v([\d\.]+)/c([\d\.]+)',link).groups()
		return vol, chapter
	@property
	def rating(self):
		rating = self.html.select_one('div[class="manga-rating__value"]').get_text()
		rating = float(rating)
		return rating
	@property
	def author(self):
		author
		
	@property
	def img_list(self):
		img_list = []
		vol_list = self.chapter_dict.keys()
		vol_list.reverse()
		for vol in vol_list:
			vol = MangaLibVol(self.title, vol)
			img_list+= vol.img_list
		
		return img_list

class MangaLibVol:
	def __init__(self, title, vol):
		print(f'v {title} {vol}')
		self.manga = MangaLibBook(title)
		self.vol = vol
		self.title = title
		
	@property	
	def img_list(self):
		self.chapter_list_for_vol = self.manga.chapter_dict.get(self.vol)
		self.chapter_list_for_vol.reverse()
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
		page = get(self.chapter_url)
		if not page.ok:
			raise Exception(f"Chapter '{title}-{vol}-{chapter}' not exists")
		self.html = BeautifulSoup(page.text, features="lxml")

	@property
	def img_list(self):
		#self.html = BeautifulSoup(download(self.chapter_url), features="lxml")
		base_code = str(self.html.select_one('span.pp'))
		base_code = re.search('<span class="pp"><!-- ([\S\d=]*) -->', base_code).group(1)
		img_list = json.loads( b64decode(base_code))
		return [f'https://img{ran(1,3)}.{self.path}/'+i.get('u') for i in img_list]
		

