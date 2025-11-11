import asyncio
from calendar import c
from typing_extensions import ChainMap
from tqdm.asyncio import tqdm_asyncio
import json
import os
import re
from bs4 import BeautifulSoup, Tag
from .Site import Site
from utils import create_path
import logging
logger = logging.getLogger(__name__)


class WeebCentral(Site):

    def __init__(self, link, name, workers) -> None:
        super().__init__(link, name, workers)

    headers = {
        'authority': 'weebcentral.com',
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
    async def get_chapters(self, last_chapter=None):
        '''gets a list of chapters until last_chapter, if last_chapter is None gets all chapters'''
        chapters = []
        link = self.link.rsplit('/', 1)[0]
        link += '/full-chapter-list'
        content = await self.fetch_text(link)
        if not content:
            logger.error('no content')
            return
        soup = BeautifulSoup(content, 'html5lib')
        chapters_elements = soup.select('a.hover\\:bg-base-300.flex-1.flex.items-center.p-2')
        for chapter_element in chapters_elements:
            chapter_name_element = chapter_element.select('.grow.flex.items-center.gap-2')
            if not chapter_name_element:
                logger.error('no number title: %s', chapter_name_element.text)
                continue
            title = chapter_name_element[0].select('span',class_=False)[0].text
            number = re.search(r' [+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)', title)
            if not number:
                logger.error('no number title: %s', title.text)
                continue
            number = float(number.group())
            if last_chapter and number <= float(last_chapter):
                break
            href = chapter_element['href']
            if not href:
                logger.error('no href item: %s', chapter_element.text)
                continue
            chapters.append({'chapter_name': title, 'href': href, 'number':number})
        return chapters

    async def _download_chapter(self, chapter, path):
        link = chapter['href']
        link += "/images?is_prev=False&current_page=1&reading_style=long_strip"
        content = await self.fetch_text(link)
        if not content:
            logger.error('no content')
            return
        soup = BeautifulSoup(content, 'html5lib')
        img = soup.select('img')
        img_src = [img['src'] for img in img]
        images = [asyncio.ensure_future(self.fetch_image(image, os.path.join(path, f'{i}.jpg')))
                  for i, image in enumerate(img_src,1)]
        await tqdm_asyncio.gather(*images, desc=f"downloading chapter: {chapter['chapter_name']}")

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
