import sys
import os
import hashlib
from send2trash import send2trash

def backspace(n):
    print('\r', end='')  

def chunk_reader(fobj, chunk_size=1024):
    """Generator that reads a file in chunks of bytes"""
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk

def get_hash(filename, first_chunk_only=False, has=hashlib.sha1):
    hashobj = has()
    with open(filename, 'rb') as file_object:
        if first_chunk_only:
            hashobj.update(file_object.read(1024))
        else:
            for chunk in chunk_reader(file_object):
                hashobj.update(chunk)
    hashed = hashobj.digest()
    file_object.close()
    return hashed

def check_for_duplicates(paths):
    hashes_by_size = {}
    hashes_on_1k = {}
    hashes_full = {}
    a = 0
    b = 0

    for path in paths:
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                b += 1
                full_path = os.path.join(dirpath, filename)
                try:
                    file_size = os.path.getsize(full_path)
                except (OSError,):
                    continue
                duplicate = hashes_by_size.get(file_size)
                if duplicate:
                    hashes_by_size[file_size].append(full_path)
                else:
                    hashes_by_size[file_size] = []  # create the list for this file size
                    hashes_by_size[file_size].append(full_path)
    print(f'Number of Files: {b}, duplicated_names {a}')

    for __, files in hashes_by_size.items():
        if len(files) < 2:
            continue
        for filename in files:
            small_hash = get_hash(filename, first_chunk_only=True)
            duplicate = hashes_on_1k.get(small_hash)
            if duplicate:
                hashes_on_1k[small_hash].append(filename)
            else:
                hashes_on_1k[small_hash] = []        
                hashes_on_1k[small_hash].append(filename)

    for __, files in hashes_on_1k.items():
        if len(files) < 2:
            continue
        for filename in sorted(files, reverse = True):
            full_hash = get_hash(filename, first_chunk_only=False)
            duplicate = hashes_full.get(full_hash)
            if duplicate:
                a += 1
                send2trash(filename)
                print(f'{b}:{a}', end = ''); backspace(len(str(f'{b}:{a}')))
            else:
                hashes_full[full_hash] = filename
    print(f'Number of Files: {b}, duplicated files {a}')
                               
paths = ['/Users/standa/eclipse-workspace/photobook/whatsup/data']
check_for_duplicates(paths)
