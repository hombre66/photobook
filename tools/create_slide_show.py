"""
create svideo form jpegd filrs 
"""

from pendulum import from_format
import piexif
from os import fwalk, makedirs, rename, path
import cv2
import os
from time import  sleep

FILES = {}

DATA_PATH = '/Users/standa/eclipse-workspace/photobook/whatsup/data/'
IN_PRINT_AUTHOR = False
IN_PRINT_DATE_FORMAT = 'DD/MM/YYYY'
CHAT_FILE_NAME = f'{DATA_PATH}/_chat.txt'
HTML_FILE_NAME = 'filip.html'
NAME = ''



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
        if not path.basename(file)[0].isdigit() and date:
            rename(file, path.join(DATA_PATH, NEW_DIR, f"{date}_{path.basename(file)}"))
            print(path.join(DATA_PATH, NEW_DIR, path.basename(file)))
    except Exception as exc:
        print(exc)



ENU = 0
 
get_files() 

for file in sorted(FILES.values()):
    prefix_created_date(file)
    ENU += 1

print('readed files', ENU)


ENU = 0

DEBUG = False

W = 1920
H = 1080

DATA_PATH = '/Users/standa/eclipse-workspace/photobook/whatsup/data/'
NEW_DIR = 'slide_show'
image_folder = path.join(DATA_PATH, NEW_DIR)
video_name = 'video.mpg4'
video = cv2.VideoWriter(video_name,  cv2.VideoWriter_fourcc(*'H264'), 0.33, (W, H))


for image in sorted([img for img in os.listdir(image_folder) if img.endswith('jpg')]):

    _image = cv2.imread(os.path.join(image_folder, image))
    
    h, w ,_ = _image.shape
    scale = min(W/w, H/h)

    
    resized = cv2.resize(_image, None, fx= scale,fy=scale , interpolation=cv2.INTER_LINEAR)
    h1, w1, _ = resized.shape
    y =H-h1
    x = W-w1
    top = y // 2
    bottom = y - top
    left = x // 2
    right = x - left
    
    padded = cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT)
    if DEBUG:
        cv2.imshow('img', padded)
        sleep(1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
   
    if padded.shape != (H, W, 3):
        ENU += 1
        print(padded.shape)
    video.write(padded)



video.release()
cv2.destroyAllWindows()
print('not procesed filrs', ENU)
