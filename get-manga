#!/bin/python
from Magazine import create_manga
from utils import get_mangas_dir
import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='get-manga.log',
                    filemode='w',
                    level=logging.DEBUG,
                    format='%(levelname)-8s %(asctime)s,%(msecs)03d [%(filename)s:%(lineno)d]\t%(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S')

async def getmanga(link, name, from_chapter):
    manga = await create_manga([link], name, from_chapter)

    chapters = await manga.get_chapters()
    if not chapters:
        logger.info(f'no chapters for {name}')
        return

    path = f'{get_mangas_dir()}/{name}'
    if not os.path.exists(path):
        os.mkdir(path)

    await manga.download(chapters, path)

if __name__ == "__main__":
    import asyncio
    import sys

    link = sys.argv[1]
    name = sys.argv[2]
    if len(sys.argv) > 3:
        from_chapter = float(sys.argv[3])
    else:
        from_chapter = None
    print(link, name, from_chapter)
    asyncio.run(getmanga(link, name, from_chapter))
