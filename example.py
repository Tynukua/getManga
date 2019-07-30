import getManga
from pprint import pprint

manga = getManga.Manga.get('mangalib.me','onepunchman')

pprint(manga.info)
pprint(manga.chapter_dict)

chapter = manga.get_chapter(1)
volume = manga.get_volume(1)
