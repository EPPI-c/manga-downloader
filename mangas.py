import requests, re, concurrent.futures, os, json
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from PIL import Image

class Site:#add new sites
    def __init__(self, link, last_chapter = None):
        #dictionary with valid sites
        self.sites = {'https://mangadex.org': Mangadex, 'https://mangakakalot.com': Mangakakalot, 'https://mangadex.tv': Mangadextv, 'https://unionmangas.top': UnionMangas, 'https://mangasee123': Mangasee}
        link.lower()
        self.last_chapter = last_chapter
        self.link = link

        for site in self.sites.keys():
            if site in self.link:
                self.__class__ = self.sites[site]
                break

        else:
            self.__class__ = None

    def get_chapters(self, last_chapter=None):
        pass

    def download_chapters(self, chapters, path=os.getcwd(), threads=3):
        '''chapters = list with json files of chapter objects
        path = path where the chapters are going to be safed'''
        pass

    def _split(self, a, n):
        k, m = divmod(len(a), n)
        return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

    def _clean_file_name(self, file_name):
        invalid = '<>:"/\|?* '

        for char in invalid:
            file_name = file_name.replace(char, '')

        return file_name

    def _run(self, path, chapters, threads, download):
        args = [(i, path) for i in self._split(chapters, threads)]
        with concurrent.futures.ThreadPoolExecutor(threads) as executor:
            executor.map(download, args)

    def _verifyimg(self, image):
        '''returns False and deletes image if image is corrupted and returns True if image is fine'''

        try:
            img = Image.open(image)
            img.verify()

        except (IOError, SyntaxError) as e:
            os.remove(image)
            print("¯\_( ͡° ͜ʖ ͡°)_/¯")
            return False

        return True

    def _request(self, url):
        request = Request(url)
        for i in self.headers.keys():
            request.add_header(i, self.headers[i])

        response = urlopen(request).read()
        return response

class Mangadex(Site):#broken
    def get_chapters(self, last_chapter=None):
        pass

    def download_chapters(self, chapters, path=os.getcwd(), threads=3):
        pass

class Mangakakalot(Site):#add exceptions, last chapter, broken
    headers = {
        'Referer': 'https://mangakakalot.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    }
    def get_chapters(self, last_chapter=None):
        r = requests.get(self.link)
        soup = BeautifulSoup(r.content, 'html5lib')
        soup = soup.find("div", class_="chapter-list")
        soup = soup.find_all(href=True)
        chapters = []
        for i in soup:
            number = re.search(r'Chapter [0-9|.]+', i.text).group().removeprefix('Chapter ')
            if number == last_chapter:
                break
            chapters.append({'chapter_name': i['title'], 'href': i['href']})

        return chapters

    def download_chapters(self, chapters, path=os.getcwd(), threads=3):# save last chapter
        def download(args):
            def downloadimg(image, path):
                r = requests.get(image['src'], headers = self.headers, stream = True)
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
                links = soup.find_all('img')
                counter = 0
                for image in links:
                    counter += 1
                    imgname = os.path.join(path, f'{counter}.jpg')
                    downloadimg(image, imgname)

                    while not self._verifyimg(imgname):
                        downloadimg(image, imgname)

        self._run(path, chapters, threads, download)

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

class Mangasee(Site):#last chapter exceptions

    headers = {
        'authority': 'mangasee123.com',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-gpc': '1',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-US,en;q=0.9',
    }
    def get_chapters(self, last_chapter=None):
        chapters = []
        name = self.link.replace('https://mangasee123.com/manga/', '')
        link = f"https://mangasee123.com/rss/{name}.xml"
        content = self._request(link)
        content = content.decode('UTF-8')
        soup = BeautifulSoup(content, 'html5lib')
        items = soup.find_all('item')
        for item in items:
            title = item.find('title')
            number = re.search(r' [+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)', title.text).group(0).removeprefix(' ')
            if number == last_chapter:
                break
            chapters.append({'chapter_name': title.text, 'href': re.search(r'https:.*\.html', item.text).group(0)})

        return chapters

    def download_chapters(self, chapters, path=os.getcwd(), threads=3):
        '''chapters = list with json files of chapter objects
        path = path where the chapters are going to be safed'''
        def download(args):
            def downloadimg(image, path):
                r = requests.get(image, stream=True)
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
                req = Request(chapter['href'])
                for i in self.headers.keys():
                    req.add_header(i, self.headers[i])
                content = urlopen(req).read()

                soup = BeautifulSoup(content, 'html5lib')
                footer = re.search(r' MainFunction.* MainFunction', str(soup), re.DOTALL).group()
                # get href
                href = soup.find('div', attrs={'ng-if': "!vm.Edd.Active"}).find('img')['ng-src']

                # get vm.CurPathName
                CurPathName = re.search(r'vm.CurPathName = ".*"', footer).group().removeprefix('vm.CurPathName = "').removesuffix('"')

                # get vm.CurChapter
                CurChapter = re.search(r'vm.CurChapter = {.*;', footer).group().removeprefix('vm.CurChapter = ').removesuffix(';')
                CurChapter = json.loads(CurChapter)

                if CurChapter['Directory'] != "":
                    Directory = CurChapter['Directory'] + '/'
                else:
                    Directory = CurChapter['Directory']

                chapterimage = self.__chapter_image(CurChapter['Chapter'])

                links = self.__get_links(href, CurPathName, Directory, chapterimage, CurChapter)
                counter = 0
                for image in links:
                    counter += 1
                    imgname = os.path.join(path, f'{counter}.jpg')
                    downloadimg(image, imgname)
                    while not self._verifyimg(imgname):
                        downloadimg(image, imgname)

        # self._run(path, chapters, threads, download)
        download([chapters, path])

    def __chapter_image(self, chapterstring):
        chapter = chapterstring[1:-1]
        if chapterstring[-1] != '0':
            chapter = chapter + '.' + chapterstring[-1]
        return chapter

    def __get_links(self, href, CurPathName, Directory, chapterimage, CurChapter):
        links = []

        def PageImage(page):
            s = '000' + page
            return s[-3:]

        def get_link(href, CurPathName, Directory, chapterimage, page):
            link = href.replace('{{vm.CurPathName}}', CurPathName)
            link = link.replace("{{vm.CurChapter.Directory == '' ? '' : vm.CurChapter.Directory+'/'}}", Directory)
            link = link.replace('{{vm.ChapterImage(vm.CurChapter.Chapter)}}', chapterimage)
            link = link.replace('{{vm.PageImage(Page)}}', page)
            return link

        for page in range(1, int(CurChapter['Page'])+1):
            page = PageImage(str(page))
            links.append(get_link(href, CurPathName, Directory, chapterimage, page))

        return links

    # def __ChapterUrlEncode(self, chapter, PageOne):

    #     t = chapter[0:1]
    #     Index = ''
    #     if t != '1':
    #         Index = '-index-' + t
    #     n = chapter[-3:-1]
    #     a = chapter[-1]
    #     m = ''
    #     if a != '0':
    #         m = f'.{a}'
    #     return ("-chapter-" + n + m + Index + PageOne + ".html", n + m)


mangas = [
            ('https://mangasee123.com/manga/Tonikaku-Kawaii', '180'), #tonikaku
            ('https://mangasee123.com/manga/Kaguya-Wants-To-Be-Confessed-To', '253'), #kaguya
            # ('https://mangasee123.com/manga/Its-Difficult-To-Love-An-Otaku', '74'), #wotakoi
            ('https://mangasee123.com/manga/Kanojo-Okarishimasu', '223'), #kanojo okarishimasu
            ('https://mangasee123.com/manga/Kakkou-no-Iinazuke', '98'), #kakkou no iinazuke
            ('https://mangasee123.com/manga/Spy-X-Family', '59'), #spy x family
            ('https://mangasee123.com/manga/Gokushufudou-The-Way-Of-The-House-Husband', '87'), #gokushufudou
            ('https://mangasee123.com/manga/Oshi-no-Ko', '70'), #oshi no ko
            ('https://unionmangas.top/manga/kao-ni-denai-kashiwada-san-to-kao-ni-deru-ota-kun', '22'), #kao ni denai kashiwada san to kao ni deru ota kun
            # ('https://mangakakalot.com/read-nq9sw158504865972', '64'), #jahy-sama
            ('https://mangasee123.com/manga/Himeno-chan-ni-Koi-Ha-Mada-Hayai', '64'), #himeno
            # ('https://mangadex.org/title/edf99f42-a1a2-458f-b482-7799872ec984', '106'), #fetiple
            # ('https://mangadex.org/title/9903ac5f-b7ef-44ec-a7fd-a971c23473fd/koi-to-uso', '278'), #koi to uso
            ('https://mangasee123.com/manga/Grand-Blue', '75'), #grand blue
            ('https://mangasee123.com/manga/Gekkan-Shojo-Nozaki-Kun', '130'), #nozaki
            ('https://mangasee123.com/manga/My-Senpai-Is-Annoying', '6'), #my senpai is annoying
            ('https://mangasee123.com/manga/Kubo-san-wa-Boku-Mobu-wo-Yurusanai', '100'), #kubo
            # ('https://mangasee123.com/manga/Life-Lessons-with-Uramichi-Oniisan', None), #uramichi
            ('https://mangasee123.com/manga/Soredemo-Ayumu-wa-Yosetekuru', '141'), #Soredemo-Ayumu-wa-Yosetekuru
            ('https://mangasee123.com/manga/Ijiranaide-Nagatoro-san', '99') #nagatoro
        ]

def main(mangas):
    manga = Site(mangas[0], last_chapter = mangas[1])
    chapters = manga.get_chapters(last_chapter=manga.last_chapter)
    manga.download_chapters(chapters, threads = 3, path = 'mangas')


for i in mangas:
    main(i)

# class MangaLivre(Site):#add excepetions, last chapter
#     headers = {
#         'authority': 'mangalivre.net',
#         'upgrade-insecure-requests': '1',
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.115 Safari/537.36',
#         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#         'sec-gpc': '1',
#         'sec-fetch-site': 'none',
#         'sec-fetch-mode': 'navigate',
#         'sec-fetch-user': '?1',
#         'sec-fetch-dest': 'document',
#         'accept-language': 'en-US,en;q=0.9',
#     }
#     def get_chapters(self, last_chapter=None):
#         regex = re.search(r'https.*/',self.link)
#         ids = self.link.replace(regex.group(0), '')
#         bool = True
#         chapters = []
#         counter = 1
#         while bool:
#             url = f'https://mangalivre.net/series/chapters_list.json?page={counter}&id_serie={ids}'
#             r = self._request(url)
#             r = json.loads(r.decode('utf-8'))
#             first_chapter = r['chapters'][0]['serieFirstChapter']
#             for i in r['chapters']:
#                 if str(last_chapter) == i['number']:
#                     bool = False
#                     break
#                 chapters.append(i)
#                 if first_chapter == i['number']:
#                     bool = False
#             counter += 1
#         return chapters

#     def download_chapters(self, chapters, path=os.getcwd(), threads=3):
#         '''chapters = list with json files of chapter objects
#         path = path where the chapters are going to be safed'''
#         def download(args):
#             def downloadimg(image, path):
#                 r = requests.get(image, stream = True)
#                 with open(path, 'wb') as f:
#                     for chunk in r:
#                         f.write(chunk)

#             #creating dir------------------------------------------
#             for chapter in args[0]:
#                 if chapter['chapter_name'] != '':
#                     path = os.path.join(args[1], self._clean_file_name(f"{chapter['name']}_{chapter['number']}_{chapter['chapter_name']}"))
#                 else:
#                     path = os.path.join(args[1], self._clean_file_name(f"{chapter['name']}_{chapter['number']}"))
#                 if not os.path.exists(path):
#                     os.mkdir(path)
#                 else:
#                     counter = 0
#                     cpath = path
#                     while os.path.exists(path):
#                         counter += 1
#                         path = cpath + f'({counter})'
#                     os.mkdir(path)
#                 #downloading-----------------------------------------------

#                 link = "https://mangalivre.net" + chapter['releases'][list(chapter['releases'].keys())[0]]['link']
#                 idc =  chapter['releases'][list(chapter['releases'].keys())[0]]['id_release']
#                 p = self._request(link)
#                 p = p.decode('utf-8')
#                 regex = re.search(r'page.identifier.*;', p.text)
#                 idp = regex.group(0).replace('page.identifier = "', '')
#                 idp = idp.removesuffix('";')
#                 url = f'https://mangalivre.net/leitor/pages/{idc}.json?key={idp}'
#                 im = requests.get(url, headers=self.headers)
#                 print(im)
#                 counter = 0
#                 for image in im.json()['images']:
#                     counter += 1
#                     imgname = os.path.join(path, f'{counter}.jpg')
#                     downloadimg(image, imgname)

#                     while not self._verifyimg(imgname):
#                         downloadimg(image, imgname)

#         self._run(path, chapters, threads, download)
