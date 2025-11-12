import json
import requests
import asyncio
from Magazine import create_manga

def gen_magazine():
    print('Write your anilist username: ')
    username = input('-> ')
    mangas = get_currently_reading(username)

    #ToDo Show error
    if(mangas == -1):
        return -1;

    magazine = gen_manga_list(mangas, username)

    with open(f"magazines/{username}_anilist.json",'w') as f:
        json.dump(magazine,f)


async def update_magazine(username):
    mangas = get_currently_reading(username)

    #ToDo Show error
    if(mangas == -1):
        return -1;

    with open(f"magazines/{username}_anilist.json",'r') as f:
        dictionary = json.load(f)
        try:
            mangasdict:dict = dictionary['mangas']
        except (KeyError, AttributeError):
            raise Exception("Magazine file is not well formatted, missing variables")

    for new_id, new_manga in mangas.items():
        old_manga = mangasdict.get(new_id) 
        if(not old_manga):
            title = gen_title(new_manga)
            print(f"New manga found: {title}")
            link = await get_link(title)
            if(link != 0):
                mangasdict[new_id] = format_manga(new_manga, title, link)
        else:
            mangasdict[new_id]['progress'] = new_manga['progress']

    dictionary['mangas'] = mangasdict

    with open(f"magazines/{username}_anilist.json",'w') as f:
        json.dump(dictionary, f)

def get_currently_reading(username):
    query = '''
        {
            Page (page: 1, perPage: 1000) {
                mediaList(userName:"'''+username+'''", status:CURRENT, type:MANGA){
                    id
                    media {
                        title {
                            english
                            romaji
                        }
                    }
                    progress
                }
            }
        }
    '''

    url = 'https://graphql.anilist.co'

    response = requests.post(url, json={'query': query})

    if(response.status_code != 200):
        return -1;

    data = json.loads(response.text)

    media_list = data['data']['Page']['mediaList']

    mangasdict = {}

    for item in media_list:
        mangasdict[item['id']] = {
            "id": item['id'],
            "english_title": item['media']['title']['english'],
            "romaji_title": item['media']['title']['romaji'],
            "progress": item['progress']
        }

    return mangasdict


def gen_manga_list(mangas:dict,username):
    mangasdict = {}

    for manga in mangas.values():

        title = gen_title(manga)
        link = asyncio.run(get_link(title))

        if(link != 0):
            mangasdict[manga['id']] = format_manga(manga, title, link) 

    magazine = {
        'mangas':mangasdict,
        'name': username + "'s anilist",
    }
    return magazine


def gen_title(manga:dict):
    if(manga['english_title'] == None):
        title = manga['romaji_title']
    elif(manga['romaji_title'] == None):
        title = manga['english_title']
    else:
        title = manga['romaji_title'] + ' (' + manga['english_title']+')'

    return title


async def get_link(title:str):

    print('Write the link for the manga: ' + title + ' (0 to Skip)')
    while True:
        link = input('-> ')

        if(link == '0'):
            return 0;

        try:
            manga = await create_manga([link], 'placeholder')
            if not await manga.test():
                raise
        except Exception as e:
            print(e)
            print('Invalid link, try again')
            continue

        return link


def format_manga(manga:dict, title:str, link:str):

    return {
            'id': manga['id'],
            'name': title,
            'link': [link],
            'progress': manga['progress'],
            'last_chapter': manga['progress']
    }
