"""
Reads What's Up export, saves it to pandas data frame
1, fix/creates Exif created date
2, in prints author and created date to image
3, creates HTML presentation
4, moves to dir by year month of Exif create date
Stanislav Vohnik 2023-02-11
"""
from os import fwalk
from pandas import DataFrame
from re import  compile as re_compile
from pendulum import from_format, datetime
from PIL import Image, ImageDraw, ImageFont
import piexif
from fnmatch import filter
from os import makedirs, rename, path
from tqdm import tqdm



CHAT_PATERN = re_compile(r'\[(\d+\.\d+\.\d+,\s+\d+:\d+:\d+)\] ([^:]+): (.*)')
ATT_PATERN = re_compile(r'<attached:\s* ([^\>]+)>')
FILES = {}




def get_files(a, b):
    for root, _dir, files,  n in fwalk(DATA_PATH):
        for file in files:
            FILES[file]= ('/'.join([root, file]))
    

def get_date(file, img):
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


def in_print(file, img):
    """
    In prints chats author and Exif created date to image
    """
    if img:
        
        wth, height = img.size
        size = int(0.021 * wth)
        date, bexif = get_date(file, None)
    
        author = ''
        if date:
            if not CHATS.empty:
                author = CHATS[["Author"]][CHATS.Day == date].values
                author = f" (Foto {author[0][0]})" if author.any() else ''
            if not IN_PRINT_AUTHOR:
                author = ''
            text = NAME + f" {date.format(IN_PRINT_DATE_FORMAT)}{author}"
            in_print = ImageDraw.Draw(img)
            in_print.text((wth - size * 10, height - size - 60), text, font=ImageFont.truetype("Arial.ttf", size=size), align="right")
            img.save(file, format=img.format, exif=bexif)
        else:
            print(file, 'no Exif date')



def set_created_date(file, img):
    """
    fix/creates Exif created date
    """
    if img:
        date, _ = get_date(file, None)
        if  not date:
            pat = re_compile(r"(\d\d\d\d)-(\d\d)-(\d\d)-(\d\d)-(\d\d)")
        
            date = datetime(*map(int, pat.findall(file)[0])).format('YYYY:MM:DD HH:mm:ss')
            bexif = piexif.dump({"Exif": {36867: date, 36868: date,}})
            img.save(file, format=img.format, exif=bexif)



def copy_to_directory_by_date(file, _):
    """
    copy files to yyyy/mm directory structure
    according exif data
    """
    try:
        date, _ = get_date(file, None)
        month = str(date.month).rjust(2, '0')
        year = str(date.year)
        new_dir = f"{year}/{month}"
        makedirs(path.join(DATA_PATH, str(year)), exist_ok=True)
        makedirs(path.join(DATA_PATH, str(year), month), exist_ok=True)
        rename(file, path.join(DATA_PATH, new_dir, path.basename(file)))
        print(path.join(DATA_PATH, new_dir, path.basename(file)))
    except Exception as exc:
        print(exc)


def get_chats():
    """
    Reads chat file and save it into pandas dataframe
    """
    try:
        with open(CHAT_FILE_NAME, 'r') as data:
            DATA = data.read()
            return DataFrame([{'Day': from_format(_date_time, 'DD.MM.YYYY, HH:mm:ss'),
                                'Author': _author ,
                                'Body': _body}
                               for _date_time, _author, _body in CHAT_PATERN.findall(DATA)])
    except FileNotFoundError as exp:
        print(exp)
        return DataFrame()


def html(a, b):
    """
    Creates web presentation form Apple's Whts Up chat export
    """
    formater = {"Day": lambda dt: str(dt)[:-6],
                "Body": lambda data: f'<img src="{FILES.get(ATT_PATERN.findall(data)[0])}" height="360" object-fit="cover">' if ATT_PATERN.findall(data) else data,
               }
    HTML = CHATS.to_html(escape=False, render_links=True, formatters=formater)
    with open(HTML_FILE_NAME, "w", encoding="utf-8") as html_file:
        html_file.writelines('<meta charset="UTF-8">\n')
        html_file.write(HTML)



def do(action):
    """
    Loop to execute action on files in directory
    """
    enu = 0
    if action == get_files:
        return action(None, None)
        
    for file in tqdm(sorted(FILES.values())):
        img = Image.open(file) if filter([file], '*.[JjMm][Pp][Gg]') else None
        action(file, img)
        enu += 1
        if img:
            img.close()
    else:
        print(f'Number of Processed Files from directory "{DATA_PATH}":', enu)


ACTIONS = [get_files,
           set_created_date,
            in_print,
            copy_to_directory_by_date,
            get_files,
            html
          ]

DATA_PATH = './data'

    
IN_PRINT_AUTHOR = False
IN_PRINT_DATE_FORMAT = 'DD/MM/YYYY'
CHAT_FILE_NAME = f'{DATA_PATH}/_chat.txt'
HTML_FILE_NAME = 'filip.html'
NAME = ''



CHATS = get_chats()

for action in ACTIONS:
    print(action)
    do(action)


