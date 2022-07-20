from .Site import Site
import requests, re, os, json
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

class Mangasee(Site):#last chapter exceptions

    def __init__(self, link) -> None:
        super().__init__(link)

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
            chapters.append({'chapter_name': title.text, 'href': re.search(r'https:.*\.html', item.text).group(0), 'number':number})

        return chapters

    def download_chapters(self, chapters, path, threads):
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