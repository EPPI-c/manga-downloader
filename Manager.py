from Downloader import Downloader
import os
import json

class Manager:

    def list_magazines(self):
        return os.listdir("magazines")
    
    def get_magazine_config(self, magazine):
        with open(magazine, 'r') as f:
            magazine = json.load(f)

        return magazine
        
    def dowload_magazine(self, magazine, path):
        for manga in magazine['mangas']:
            dowloader = Downloader(manga['link'])
            chapter_list = dowloader.get_chapters(manga['last_chapter'])
            dowloader.dowload_chapters(chapter_list, path)

    def update_last_chapter(self):
        pass


if __name__ == "__main__":
    manager = Manager()

    magazine = manager.get_magazine_config('magazines/myjump.json')

    manager.dowload_magazine(magazine, path='mangas')