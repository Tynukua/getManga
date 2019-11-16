# getManga
Tool for load manga from different websites


_I_ _just_ _wanted_ _to_ _read_ _the_ _manga..._

import main class:
```Python
from getManga import Manga
```


```Python
async def main():
    site = 'mangalib.me' # Website's domen
    title = 'shingeki-no-kyojin' #unique name
    link = 'https://mangalib.me/shingeki-no-kyojin'
    # Inislization:
    manga = await Manga.get(site,title).parse()
    manga2 = await Manga(link).parse()


    # Methods:

    manga.info 				#some information about manga
    manga.img_list 				#return links for pages(take many time for work)
    manga.chapter_list			#return list of (volume_number, chapter_number, chapter_name)
    manga.chapter_dict			#return dict {volume_numbers: {chapter_numbers: chapter_name}}

    chapter = manga.get_chapter(int) 	#return chapter №int
    volume = manga.get_volume(int) 		#return volume №int

    await chapter.img_list			#return links for pages from volume
    await volume.img_list  			#return links for pages from volume

#Start parsing
if __name__ == "__main__":
    loop = get_event_loop()
    loop.run_until_complete(main())
```

