from .Site import Site
import requests, re, os
from bs4 import BeautifulSoup

class Manganato(Site):#add exceptions, last chapter, broken

    def __init__(self, link) -> None:
        super().__init__(link)

    headers = {
        'Referer': 'https://manganato.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    }
    def get_chapters(self, last_chapter=None):
        r = requests.get(self.link)
        soup = BeautifulSoup(r.content, 'html5lib')
        soup = soup.find("ul", class_="row-content-chapter")
        soup = soup.find_all(href=True)
        chapters = []
        for i in soup:
            try:
                number = re.search(r'(chapter)-?[0-9|.]+', i['href']).group().removeprefix('chapter-')
            except:
                continue
            if number == last_chapter:
                break
            chapters.append({'chapter_name': i['title'], 'href': i['href'], 'number':number})

        return chapters

    def download_chapters(self, chapters, path=os.getcwd(), threads=3):# save last chapter
        def download(args):
            def downloadimg(image, path):
                r = requests.get(image, headers = self.headers, stream = True)
                with open(path, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)

            for chapter in args[0]:
                path = os.path.join(args[1], self._clean_file_name(chapter['chapter_name']))
                if not os.path.exists(path):
                    os.mkdir(path)
                else:
                    counter = 0
                    cpath = path
                    while os.path.exists(path):
                        counter += 1
                        path = cpath + f'({counter})'
                    os.mkdir(path)
                r = requests.get(chapter['href'])
                soup = BeautifulSoup(r.content, 'html5lib')
                soup = soup.find("div", class_="container-chapter-reader")
                soup = soup.find_all('img')
                links = []
                for i in soup:
                    links.append(i['src'])
                counter = 0
                for image in links:
                    counter += 1
                    imgname = os.path.join(path, f'{counter}.jpg')
                    downloadimg(image, imgname)

                    while not self._verifyimg(imgname):
                        downloadimg(image, imgname)

        self._run(path, chapters, threads, download)