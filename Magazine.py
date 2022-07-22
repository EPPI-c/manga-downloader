from os.path import join as join_path
from os import getcwd

import yaml

import sites

class Manga():
    def __init__(self, link, name, last_chapter=None, provider=None):
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

    def dowload_chapters(self, chapters, path=getcwd(), threads=3):
        return self.site.download_chapters(chapters, path, threads)

    def get_chapters(self, until_last=True):
        """gets chapters of this manga"""
        if until_last:
            return self.site.get_chapters(self.last_chapter)
        else:
            return self.site.get_chapters()

    def __dict__(self):
        """transforms object in dictionary"""
        return {'name':self.name, 'link':self.link,'last_chapter':self.last_chapter, 'provider':self.provider}

    def download(self, chapter_list, path=getcwd(), threads=3, update_last_chapter=True):
        if update_last_chapter:
            response = self.site.download_chapters(chapter_list, path, threads)
            self.last_chapter = chapter_list[0]['number']
            return response
        else:
            return self.site.download_chapters(chapter_list, path, threads)


class Magazine():
    def __init__(self, name=None, mangas=None, path=None):
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

    def get_all_chapters(self, until_last=True) -> dict:
        """gets chapters from all mangas in this magazine"""
        return {manga: manga.get_all_chapters(until_last) for manga in self.mangas}

    def __dict__(self):
        """transforms object in dictionary"""
        return {'name': self.name, 'mangas':{manga.name:manga.__dict__() for manga in self.mangas}}

    def update(self):
        """safes the object to yaml file"""
        with open(self.path, 'w') as f:
            yaml.dump(self.__dict__(), f)

    def download(self, chapter_list, path=getcwd(), threads=3, update_last_chapter=True):
        for manga, chapters in chapter_list:
            manga.download(chapters, path, threads, update_last_chapter)
