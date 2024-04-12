from os import fwalk
from pandas import DataFrame
from re import  compile as re_compile
from pendulum import from_format, datetime
from PIL import Image, ImageDraw, ImageFont
import piexif
from fnmatch import filter
from os import makedirs, rename, path
from tqdm import tqdm
import cv2
import os


FILES = {}

DATA_PATH = '/Users/standa/eclipse-workspace/photobook/whatsup/data'
IN_PRINT_AUTHOR = False
IN_PRINT_DATE_FORMAT = 'DD/MM/YYYY'
CHAT_FILE_NAME = f'{DATA_PATH}/_chat.txt'
HTML_FILE_NAME = 'filip.html'
NAME = ''

NEW_DIR = 'slide_show'

def get_date(file):
    """
    Gets Exif DateTimeOriginal
    """
    exif = piexif.load(file)
    _exif = exif.get('Exif', {})
    if _exif.get(36867):
        _date = _exif.get(36867).decode('utf8')
        bexif = piexif.dump(exif)
        return from_format(_date, 'YYYY:MM:DD HH:mm:ss'), bexif
    return None, None


def get_files():
    for root, _dir, files, _ in fwalk(DATA_PATH):
        print(root)
        for file in files:
            FILES[file]= ('/'.join([root, file]))
    


def prefix_created_date(file):
    """

    """
    try:
        date, _ = get_date(file)

        makedirs(path.join(DATA_PATH, NEW_DIR), exist_ok=True)
        if not path.basename(file)[0].isdigit():
            rename(file, path.join(DATA_PATH, NEW_DIR, f"{date}_{path.basename(file)}"))
            print(path.join(DATA_PATH, NEW_DIR, path.basename(file)))
    except Exception as exc:
        print(exc)



ENU = 0
 
# get_files() 
#
# for file in tqdm(sorted(FILES.values())):
#     prefix_created_date(file)
#     ENU += 1
#
# print(ENU)
#





image_folder = path.join(DATA_PATH, NEW_DIR)
video_name = 'video.mpg'



video = cv2.VideoWriter(video_name, 0, 2, (1920, 1090))

for image in sorted([img for img in os.listdir(image_folder) if img.endswith('jpg')]):
    _image = cv2.imread(os.path.join(image_folder, image))
    w,h, _ = _image.shape
    scale = min(1920/w, 1080/h)
    resized_up = cv2.resize(_image, None, fx= 1,fy=scale , interpolation= cv2.INTER_CUBIC)
    video.write(_image)

cv2.destroyAllWindows()
print(dir(video))
video.release()