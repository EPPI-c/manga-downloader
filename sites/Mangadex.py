import asyncio
from tqdm.asyncio import tqdm_asyncio
from .Site import Site
import os

class Mangadex(Site):#add exceptions, last chapter, broken

    def __init__(self, link, name, workers) -> None:
        super().__init__(link, name, workers)

    headers = {
        'Referer': 'https://mangadex.org/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    }
    async def get_chapters(self, last_chapter):
        id = self.link.split('/')[4]
        link = f'https://api.mangadex.org/manga/{id}/feed'
        r = await self.fetch_json(link)
        if not r: return
        if not (r:=r.get('data')): return
        chapters_all = sorted(filter(self._filter_en_chapters, r), key=lambda x: float(x['attributes']['chapter']), reverse=True)
        chapters = []
        for chapter in chapters_all:
            if not (chap_num := chapter['attributes'].get('chapter')): continue
            number = float(chap_num)
            title = self.name + '-' + str(number)
            if number <= float(last_chapter): break
            if not (chapter_id := chapter.get('id')): continue
            chapters.append({'chapter_name': title, 'href': f'https://api.mangadex.org/at-home/server/{chapter_id}', 'number':number})
        return chapters

    def _filter_en_chapters(self, x):
        if not (x:=x.get('attributes')): return False
        if not (x:=x.get('translatedLanguage')): return False
        if x != 'en': return False
        return True

    async def download_chapters(self, chapters, opath):# save last chapter
        for chapter in chapters:
            path = os.path.join(opath, self._clean_file_name(chapter['chapter_name']))
            if not os.path.exists(path):
                os.mkdir(path)
            else: # create duplicate with (n)
                counter = 0
                cpath = path
                while os.path.exists(path):
                    counter += 1
                    path = cpath + f'({counter})'
                os.mkdir(path)

            r = await self.fetch_json(chapter['href'])
            if not r: continue

            if not (r:=r.get('chapter')): continue
            if not (hash:=r.get('hash')): continue
            if not (r:=r.get('data')): continue
            images = map(lambda x: f'https://uploads.mangadex.org/data/{hash}/{x}', r)

            counter = 0
            images = [asyncio.ensure_future(self.fetch_image(image, os.path.join(path, f'{i}.jpg')))
                      for i, image in enumerate(images,1)]
            await tqdm_asyncio.gather(*images, desc=f"downloading chapter: {chapter['chapter_name']}")
