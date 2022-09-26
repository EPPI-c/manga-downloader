import os

import yaml

from Magazine import Magazine


class Manager:

    def list_magazines(self):
        return os.listdir("magazines")
    


    # def dowload_magazine(self, magazine:Magazine, path):
    #     for name, manga in magazine['mangas'].items():
    #         dowloader = Downloader(manga['link'])
    #         chapter_list = dowloader.get_chapters(manga['last_chapter'])
    #         if chapter_list:
    #             dowloader.dowload_chapters(chapter_list, path)
    #             self.update_last_chapter(name, chapter_list[0]['number'], magazine)

    def update_last_chapter(self, manga, number, magazine):
        magazine['mangas'][manga]['last_chapter'] = number
        with open('myjump.json', 'w') as f:
            yaml.dump(magazine, f)

if __name__ == "__main__":
    PATH = os.path.join('magazines','myjump.yaml')
    # manager = Manager()

    magazine = Magazine(path=PATH)
    chapters = magazine.get_all_chapters()

    magazine.download(chapter_dict=chapters, path='mangas')
    # print(magazine.mangas)

    # magazine = Magazine(path = PATH)
    # print(magazine.__dict__())
