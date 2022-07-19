import sites as sites


class Downloader:
    def __init__(self, link) -> None:
        self.link = link
        self.sites = {'https://mangasee123': sites.Mangasee}
        for link, site in self.sites.items():
            if link in self.link:
                self.site = site(self.link)

    def get_chapters(self, last_chapter=None):
        return self.site.get_chapters(last_chapter)



if __name__ == "__main__":
    downloader = Downloader('https://mangasee123.com/manga/Tonikaku-Kawaii')
    print(downloader.get_chapters())