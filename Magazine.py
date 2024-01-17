from tqdm.asyncio import tqdm_asyncio
import datetime
from utils import create_path
import asyncio
from os.path import exists as path_exists, join as join_path
from os import mkdir
import yaml
import sites
from sites.Site import create_site

SITES={
        'https://mangasee123': sites.Mangasee,
        'https://mangakakalot': sites.Mangakakalot,
        'https://manganato':sites.Manganato,
        'https://chapmanganato.com':sites.Manganato,
        'https://chapmanganelo.com':sites.Manganato,
        'https://mangadex.org':sites.Mangadex
        }

async def create_manga(links:list, name:str, last_chapter:str|None=None):
    manga = Manga(links, name, last_chapter)
    await manga.init()
    return manga

class Manga():
    def __init__(self, links:list, name:str, last_chapter:str|None):
        self.name = name
        self.links = links
        self.last_chapter = last_chapter
        self.sites:list[sites.Site] = []

    async def init(self):
        for site_link, site in SITES.items():
            for link in self.links:
                if site_link in link:
                    self.sites.append(await create_site(site, link, self.name))
                    break
        if not self.sites:
            raise Exception('Site not supported')

    def update_last_chapter(self, chapter_list:list):
        if not chapter_list: return 0
        self.last_chapter = chapter_list[0]['number']

    def __find_max(self, x):
        if len(x) < 2: return 0
        if not x[1]: return 0
        if (n:=x[1][0].get('number')): return 0
        return n

    async def get_chapters(self, until_last:bool=True):
        """gets chapters of this manga"""
        if until_last: last = self.last_chapter
        else: last = None
        tasks = [asyncio.ensure_future(site.get_chapters(last)) for site in self.sites]
        providers_chapters = await tqdm_asyncio.gather(*tasks, desc='getting chapters')
        index = max((i for i in enumerate(providers_chapters)), key=self.__find_max)[0]
        self.site = self.sites[index]
        return providers_chapters[index][::-1]

    async def download(self, chapter_list:list, path:str|None=None, update_last_chapter:bool=True):
        if not chapter_list: return 0
        if not path: path = join_path('mangas', self.name)
        if not path_exists(path):
            mkdir(path)
        response = await self.site.download_chapters(chapter_list, path)
        if update_last_chapter: self.last_chapter = chapter_list[-1]['number']
        return response

    def __dict__(self):
        """transforms object in dictionary"""
        return {'name':self.name, 'link':self.links,'last_chapter':self.last_chapter}


async def create_magazine(name:str|None=None, mangas:list[Manga]|None=None, path:str|None=None):
    magazine = Magazine(name, mangas, path)
    await magazine.init()
    return magazine

class Magazine():
    def __init__(self, name:str|None=None, mangas:list[Manga]|None=None, path:str|None=None):
        if path:
            self.path = path
            with open(path, 'r') as f:
                dictionary = yaml.safe_load(f)
            try:
                self.name = dictionary['name']
                self.mangasdict = dictionary['mangas']
            except (KeyError, AttributeError):
                raise Exception("Magazine file is not well formatted, missing variables")

        elif name and mangas:
            self.name = name
            self.mangas = mangas
            self.path = join_path('magazines', f'{name}.yaml')
            self.update()

        else: raise Exception('Must provide path or name and mangas')


    async def init(self):
        self.mangas = [await create_manga(manga['link'], name, manga.get('last_chapter') ) for name, manga in self.mangasdict.items()]

    async def get_all_chapters(self, until_last:bool=True) -> dict:
        """gets chapters from all mangas in this magazine"""
        mangas = []
        tasks = []
        for manga in self.mangas:
            tasks.append(asyncio.ensure_future(manga.get_chapters(until_last)))
            mangas.append(manga)
        chapter_list = await asyncio.gather(*tasks)
        return {manga:chapters for manga, chapters in zip(mangas, chapter_list)}

    def __dict__(self):
        """transforms object in dictionary"""
        return {'name': self.name, 'mangas':{manga.name:manga.__dict__() for manga in self.mangas}}

    def update_last_chapter(self, chapter_dict:dict[Manga, list]):
        for manga, chapters in chapter_dict.items():
            manga.update_last_chapter(chapters)

    def update(self):
        
        """safes the object to yaml file"""
        with open(self.path, 'w') as f:
            yaml.dump(self.__dict__(), f)

    async def download(self, chapter_dict:dict[Manga, list], path:str, update_last_chapter:bool=True):
        s = datetime.date.today()
        path = join_path(path, str(s))
        path = create_path(path)
        tasks = [manga.download(chapters, path, update_last_chapter) for manga, chapters in chapter_dict.items()]
        await asyncio.gather(*tasks)
        if update_last_chapter:
            self.update()

async def test():
    links = ['https://mangasee123.com/manga/Mikakunin-de-Shinkoukei']
    manga = await create_manga(links, 'mikakunin', '175')
    chapters = await manga.get_chapters()
    if not chapters: exit()
    print(yaml.dump(chapters))
    # chapters = await manga.download(chapters)

async def main():
    PATH = join_path('magazines','myjump.yaml')
    magazine = await create_magazine(path=PATH)
    chapters = await magazine.get_all_chapters()
    await magazine.download(chapters, 'mangas')


if __name__ == "__main__":
    asyncio.run(main())

