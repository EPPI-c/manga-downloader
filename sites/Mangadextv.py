import Site
import requests, re, os
from bs4 import BeautifulSoup

class Mangadextv(Site):#last chapter and exception handling

    def get_chapters(self, last_chapter=None):
        r = requests.get(self.link)
        soup = BeautifulSoup(r.content, 'html5lib')
        soup = soup.find('div', class_='chapter-container')
        soup = soup.find_all(href=True)
        chapters = []
        for i in soup:
            number = re.search(r'Chapter.*?[0-9|.]+', i.text).group()
            number = re.search(r'[0-9|.]+', number).group()
            print(number)
            if number == last_chapter:
                break
            chapters.append({'chapter_name': i.text, 'href': i['href']})

        return chapters

    def download_chapters(self, chapters, path=os.getcwd(), threads=3):# and save last chapter

        '''chapters = list with json files of chapter objects
        path = path where the chapters are going to be safed'''
        def download(args):
            def downloadimg(image, path):
                r = requests.get(image['data-src'], stream = True)
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
                soup = soup.find('div', class_="reader-images col-auto row no-gutters flex-nowrap m-auto text-center cursor-pointer directional")
                counter = 0
                for image in soup.find_all(class_='noselect nodrag cursor-pointer img-loading'):
                    counter += 1
                    imgname = os.path.join(path, f'{counter}.jpg')
                    downloadimg(image, imgname)
                    while not self._verifyimg(imgname):
                        downloadimg(image, imgname)

        self._run(path, chapters, threads, download)