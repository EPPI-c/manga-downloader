import os
import asyncio
import aiohttp

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

    async def download_chapters(self, chapters, path):
        '''chapters = list with json files of chapter objects
        path = path where the chapters are going to be safed'''
        pass

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

    async def fetch_text(self, url):
        async with self.sem:
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    return await resp.text()

    async def fetch_image(self, url, path, maxtries=4):
        async with self.sem:
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    with open(path, 'wb') as fd:
                        async for chunk in resp.content.iter_chunked(10):
                            fd.write(chunk)
        counter = 1
        while not self._verifyimg(path) and counter<maxtries:
            counter += 1
            await self.fetch_image(url, path)
