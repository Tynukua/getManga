import getmanga
from pprint import pprint
from asyncio import get_event_loop, wait, create_task

async def premain():
    manga = await getmanga.Manga('https://mangalib.me/dr-stone').parse()
    pprint(await manga.img_list)

loop = get_event_loop()

async def main():
    for i in range(1):
        await premain()
        
loop.run_until_complete(main())