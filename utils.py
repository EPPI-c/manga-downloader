import os
from yaml import safe_load

def create_path(path):
    '''creates path without overwriting if exists but adding (n) instead'''
    if not os.path.exists(path): os.mkdir(path)
    else:
        counter = 0
        cpath = path
        while os.path.exists(path):
            counter += 1
            path = cpath + f'({counter})'
        os.mkdir(path)
    return path


def open_config():
    with open('config.yaml', 'r') as config:
        yaml_config = safe_load(config)

    return yaml_config


def get_magazines_dir():
    return open_config()['magazines_dir']


def get_mangas_dir():
    return open_config()['mangas_dir']