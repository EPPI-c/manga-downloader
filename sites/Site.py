import os
import asyncio
import aiohttp
import logging

logger = logging.getLogger(__name__)

from PIL import Image

async def create_site(site, link, name, workers=3):
    site = site(link, name, workers)
    await site.init()
    return site

class Site:

    def __init__(self, link, name, workers) -> None:
        self.link = link
        self.name = name
        self.sem = asyncio.Semaphore(workers)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    }
    async def init(self):
        self.session = aiohttp.ClientSession()
        self.session.headers.update(self.headers)


    async def get_chapters(self, last_chapter=None):
        '''gets a list of chapters until last_chapter, if last_chapter is None gets all chapters'''
        pass

    async def _download_chapter(self, chapter, path):
        pass

    async def download_chapters(self, chapters, opath):
        '''chapters = list with json files of chapter objects
        path = path where the chapters are going to be safed'''
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
            await self._download_chapter(chapter, path)


    def _clean_file_name(self, file_name):
        invalid = r'<>:"/\|?* '

        for char in invalid:
            file_name = file_name.replace(char, '')

        return file_name

    def _verifyimg(self, image):
        '''returns False and deletes image if image is corrupted and returns True if image is fine'''

        try:
            img = Image.open(image)
            img.verify()

        except (IOError, SyntaxError):
            os.remove(image)
            return False

        return True

    async def fetch_json(self, url):
        async with self.sem:
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logger.error(f'{resp.status} response for {url}')

    async def fetch_text(self, url):
        async with self.sem:
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    return await resp.text()
                else:
                    logger.error(f'{resp.status} response for {url}')

    async def fetch_image(self, url, path, maxtries=10):
        async with self.sem:
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    with open(path, 'wb') as fd:
                        async for chunk in resp.content.iter_chunked(10):
                            fd.write(chunk)
                else:
                    logger.error(f'{resp.status} response for {url}')
        counter = 1
        while counter<maxtries:
            if not self._verifyimg(path):
                break
            counter += 1
            await self.fetch_image(url, path)
        else:
            logger.warning(f'image at {path} corrupted')
