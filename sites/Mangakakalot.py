import asyncio
from tqdm.asyncio import tqdm_asyncio
from .Site import Site
import re, os
from bs4 import BeautifulSoup, Tag

class Mangakakalot(Site):

    def __init__(self, link, name, workers) -> None:
        super().__init__(link, name, workers)

    headers = {
        'Referer': 'https://mangakakalot.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    }
    async def get_chapters(self, last_chapter):
        r = await self.fetch_text(self.link)
        if not r: return
        soup = BeautifulSoup(r, 'html5lib')
        soup = soup.find("div", class_="chapter-list")
        if not isinstance(soup, Tag): return
        soup = soup.find_all(href=True)
        chapters = []
        for i in soup:
            try:
                chap_num = re.search(r'((c|C)hapter?)(_| |-)?[0-9|.]+', i['href'])
                if not chap_num: continue
                chap_num = chap_num.group()
                number = float(re.sub(r'((c|C)hapter?)(_| |-)?','',chap_num))
                title = self.name + '-' + str(number)
            except:
                continue
            if last_chapter and number <= float(last_chapter):
                break
            chapters.append({'chapter_name': title, 'href': i['href'], 'number':number})

        return chapters

    async def _download_chapter(self, chapter, path):
        r = await self.fetch_text(chapter['href'])
        if not r: return
        soup = BeautifulSoup(r, 'html5lib')
        soup = soup.find("div", class_="container-chapter-reader") 
        if not isinstance(soup, Tag): return
        soup = soup.find_all('img')
        images = [asyncio.ensure_future(self.fetch_image(image.get('src'), os.path.join(path, f'{i}.jpg')))
                  for i, image in enumerate(soup,1)]
        await tqdm_asyncio.gather(*images, desc=f"downloading chapter: {chapter['chapter_name']}")
