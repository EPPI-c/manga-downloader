import Site
import requests, re, os
from bs4 import BeautifulSoup



class UnionMangas(Site):#last chapter exceptions

    def get_chapters(self, last_chapter=None):
        r = requests.get(self.link)
        soup = BeautifulSoup(r.content, 'html5lib')
        chapter_container = soup.find_all('div', class_='col-xs-6 col-md-6')
        title = soup.find('title')
        links = []
        for i in chapter_container:
            links.append(i.find(href=True))
        chapters = []
        for i in links:
            number =  re.search(r'Cap\. [0-9|.]+', i.text).group().removeprefix('Cap. ')
            if number == last_chapter:
                break
            chapters.append({'chapter_name': title.text + " " + i.text, 'href': i['href']})
        return chapters

    def download_chapters(self, chapters, path=os.getcwd(), threads=3):# last chapter exceptions

        '''chapters = list with json files of chapter objects
        path = path where the chapters are going to be safed'''
        def download(args):
            def downloadimg(image, path):
                r = requests.get(image['src'], stream=True)
                with open(path, 'wb') as f:
                    for chunks in r:
                        f.write(chunks)

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
                soup = soup.find_all('img')
                counter = 0
                for image in soup:
                    counter += 1
                    imgname = os.path.join(path, f'{counter}.jpg')
                    downloadimg(image, imgname)
                    while not self._verifyimg(imgname):
                        downloadimg(image, imgname)

            self._run(path, chapters, threads, download)