import os

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
