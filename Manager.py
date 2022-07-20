from Downloader import Downloader
import os
import yaml

class Manager:

    def list_magazines(self):
        return os.listdir("magazines")
    
    def get_magazine_config(self, magazine):
        with open(magazine, 'r') as f:
            magazine = yaml.safe_load(f)

        return magazine
        
    def get_chapters(self, magazine):
        chapter_list = {}
        for manga in magazine['mangas']:
            dowloader = Downloader(manga['link'])
            chapter_list[manga['name']] = dowloader.get_chapters(manga['last_chapter'])
        return chapter_list

    def dowload_magazine(self, magazine, path):
        for name, manga in magazine['mangas'].items():
            dowloader = Downloader(manga['link'])
            chapter_list = dowloader.get_chapters(manga['last_chapter'])
            if chapter_list:
                dowloader.dowload_chapters(chapter_list, path)
                self.update_last_chapter(name, chapter_list[0]['number'], magazine)

    def update_last_chapter(self, manga, number, magazine):
        magazine['mangas'][manga]['last_chapter'] = number
        with open('myjump.json', 'w') as f:
            yaml.dump(magazine, f)

if __name__ == "__main__":
    PATH = 'magazines/myjump.yaml'
    manager = Manager()

    magazine = manager.get_magazine_config(PATH)
    manager.dowload_magazine(magazine, path='mangas')