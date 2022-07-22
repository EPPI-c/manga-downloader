import concurrent.futures
import os
from urllib.request import Request, urlopen

from PIL import Image


class Site:

    def __init__(self, link) -> None:
        self.link = link

    def get_chapters(self, last_chapter=None):
        pass

    def download_chapters(self, chapters, path, threads=3):
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

        except (IOError, SyntaxError):
            os.remove(image)
            # raise Exception('image Corrupted')
            return False

        return True

    def _request(self, url):
        request = Request(url)
        for i in self.headers.keys():
            request.add_header(i, self.headers[i])

        response = urlopen(request).read()
        return response
