#!/bin/python
from Magazine import create_manga
import json
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='get-chapters.log',
                    filemode='w',
                    level=logging.DEBUG,
                    format='%(levelname)-8s %(asctime)s,%(msecs)03d [%(filename)s:%(lineno)d]\t%(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S')

async def getchapters(link, from_chapter):
    manga = await create_manga([link], 'temp', from_chapter)

    chapters = await manga.get_chapters()
    if not chapters:
        logger.error('no chapters')
        return
    print(json.dumps(chapters, indent=4))

if __name__ == "__main__":
    import asyncio
    import sys

    link = sys.argv[1]
    if len(sys.argv) > 2:
        from_chapter = float(sys.argv[2])
    else:
        from_chapter = None
    print(link, from_chapter)
    asyncio.run(getchapters(link, from_chapter))
