import asyncio
from .Site import Site
import re, os
from bs4 import BeautifulSoup

class Mangakakalot(Site):#add exceptions, last chapter, broken

    def __init__(self, link, name, workers) -> None:
        super().__init__(link, name, workers)

    headers = {
        'Referer': 'https://mangakakalot.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    }
    async def get_chapters(self, last_chapter=None):
        r = await self.fetch_text(self.link)
        if not r: return
        soup = BeautifulSoup(r, 'html5lib')
        soup = soup.find("div", class_="chapter-list")
        soup = soup.find_all(href=True)
        chapters = []
        for i in soup:
            try:
                chap_num = re.search(r'((c|C)hapter?)(_| |-)?[0-9|.]+', i['href']).group()
                number = float(re.sub(r'((c|C)hapter?)(_| |-)?','',chap_num))
                title = self.name + '-' + str(number)
            except:
                continue
            if number == float(last_chapter):
                break
            chapters.append({'chapter_name': title, 'href': i['href'], 'number':number})

        return chapters

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

            r = await self.fetch_text(chapter['href'])
            if not r: return
            soup = BeautifulSoup(r, 'html5lib')
            soup = soup.find("div", class_="container-chapter-reader") 
            soup = soup.find_all('img')
            counter = 0
            images = [asyncio.ensure_future(self.fetch_image(image.get('src'), os.path.join(path, f'{i}.jpg')))
                      for i, image in enumerate(soup,1)]
            await asyncio.gather(*images)
