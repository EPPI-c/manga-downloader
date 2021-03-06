import os


import sites


class Downloader:
    def __init__(self, link) -> None:
        self.link = link
        site_list = {'https://mangasee123': sites.Mangasee}
        for link, site in site_list.items():
            if link in self.link:
                self.site = site(self.link)

    def get_chapters(self, last_chapter=None):
        return self.site.get_chapters(last_chapter)

    def dowload_chapters(self, chapters, path=os.getcwd(), threads=3):
        return self.site.download_chapters(chapters, path, threads)


if __name__ == "__main__":
    downloader = Downloader('https://mangasee123.com/manga/Tonikaku-Kawaii')
    print(downloader.get_chapters())
