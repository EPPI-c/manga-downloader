#!/bin/python
from Magazine import create_manga
import json

async def getchapters(link, from_chapter):
    manga = await create_manga([link], 'temp', from_chapter)

    chapters = await manga.get_chapters()
    if not chapters: return
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
