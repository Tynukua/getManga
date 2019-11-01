import getmanga
from pprint import pprint
from asyncio import get_event_loop, wait

async def main():
    manga = await getmanga.Manga('https://mangalib.me/dr-stone').parse()
    print(manga)
    ch = manga.get_chapter(125)
    print(len(await ch.img_list))
loop = get_event_loop()

loop.run_until_complete(main())