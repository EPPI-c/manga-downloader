from os.path import join as join_path
from os import getcwd

import yaml

import sites

class Manga():
    def __init__(self, link:str, name:str, last_chapter:str=None, provider:str=None):
        self.name = name
        self.link = link
        self.last_chapter = last_chapter
        self.provider = provider

        for link, site in {'https://mangasee123': sites.Mangasee}.items():
            if link in self.link:
                self.site = site(self.link)
                break
        else:
            raise Exception('Site not supported')

    def dowload_chapters(self, chapters:list, path:str=getcwd(), threads:int=3):
        return self.site.download_chapters(chapters, path, threads)

    def update_last_chapter(self, chapter_list:list):
        if not chapter_list: return 0
        self.last_chapter = chapter_list[0]['number']

    def get_chapters(self, until_last:bool=True):
        """gets chapters of this manga"""
        if until_last:
            return self.site.get_chapters(self.last_chapter)
        else:
            return self.site.get_chapters()

    def __dict__(self):
        """transforms object in dictionary"""
        return {'name':self.name, 'link':self.link,'last_chapter':self.last_chapter, 'provider':self.provider}

    def download(self, chapter_list:list, path:str=None, threads:int=3, update_last_chapter:bool=True):
        if not chapter_list: return 0
        if not path: path = join_path('mangas', self.name)
        if update_last_chapter:
            response = self.site.download_chapters(chapter_list, path, threads)
            self.last_chapter = chapter_list[0]['number']
            return response
        else:
            return self.site.download_chapters(chapter_list, path, threads)


class Magazine():
    def __init__(self, name:str=None, mangas:list[Manga]=None, path:str=None):
        if path:
            self.path = path
            with open(path, 'r') as f:
                dictionary = yaml.safe_load(f)
            try:
                self.name = dictionary['name']
                self.mangas = [Manga(manga['link'], name, manga.get('last_chapter'), manga.get('provider')) for name, manga in dictionary['mangas'].items()]
            except (KeyError, AttributeError):
                raise Exception("Magazine file is not well formatted, missing variables")

        elif name and mangas:
            self.name = name
            self.mangas = mangas
            self.path = join_path('magazines', f'{name}.yaml')
            self.update()

        else: raise Exception('Must provide path or name and mangas')

    def get_all_chapters(self, until_last:bool=True) -> dict:
        """gets chapters from all mangas in this magazine"""
        return {manga: manga.get_chapters(until_last) for manga in self.mangas}

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

    def download(self, chapter_dict:dict[Manga, list], path:str=getcwd(), threads:int=3, update_last_chapter:bool=True):
        for manga, chapters in chapter_dict.items():
            manga.download(chapters, path, threads, update_last_chapter)
        if update_last_chapter:
            self.update()
