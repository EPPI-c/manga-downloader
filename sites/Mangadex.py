import asyncio
from tqdm.asyncio import tqdm_asyncio
from .Site import Site
import os

class Mangadex(Site):

    def __init__(self, link, name, workers) -> None:
        super().__init__(link, name, workers)

    headers = {
        'Referer': 'https://mangadex.org/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    }
    async def get_chapters(self, last_chapter):
        id = self.link.split('/')[4]
        link = f'https://api.mangadex.org/manga/{id}/feed?limit=96&includes[]=scanlation_group&includes[]=user&order[volume]=desc&order[chapter]=desc&offset=0&contentRating[]=safe&contentRating[]=suggestive&contentRating[]=erotica&contentRating[]=pornographic'

        r = await self.fetch_json(link)
        if not r: return
        if not (data:=r.get('data')): return
        if (total:=r.get('total')) is None: return
        if (offset:=r.get('offset')) is None: return

        # repeat until get all chapters
        while total > len(data):
            link = f'https://api.mangadex.org/manga/{id}/feed?limit=96&includes[]=scanlation_group&includes[]=user&order[volume]=desc&order[chapter]=desc&offset={offset+96}&contentRating[]=safe&contentRating[]=suggestive&contentRating[]=erotica&contentRating[]=pornographic'
            r = await self.fetch_json(link)
            if not r: break
            tmp = r.get('data')
            if not tmp: break
            data += tmp
            if (total:=r.get('total')) is None: break
            if (offset:=r.get('offset')) is None: break

        chapters_all = filter(self.__filter_en_chapters, data)
        chapters = []
        for chapter in chapters_all:
            if not (chap_num := chapter['attributes'].get('chapter')): continue
            number = float(chap_num)
            title = self.name + '-' + str(number)
            if last_chapter and number <= float(last_chapter): break
            if not (chapter_id := chapter.get('id')): continue
            chapters.append({'chapter_name': title, 'href': f'https://api.mangadex.org/at-home/server/{chapter_id}', 'number':number})
        return chapters

    def __filter_en_chapters(self, x):
        if not (x:=x.get('attributes')): return False
        if not (x:=x.get('translatedLanguage')): return False
        if x != 'en': return False
        return True

    async def _download_chapter(self, chapter, path):
        r = await self.fetch_json(chapter['href'])
        if not r: return

        if not (r:=r.get('chapter')): return
        if not (hash:=r.get('hash')): return
        if not (r:=r.get('data')): return
        images = map(lambda x: f'https://uploads.mangadex.org/data/{hash}/{x}', r)

        images = [asyncio.ensure_future(self.fetch_image(image, os.path.join(path, f'{i}.jpg')))
                  for i, image in enumerate(images,1)]
        await tqdm_asyncio.gather(*images, desc=f"downloading chapter: {chapter['chapter_name']}")
