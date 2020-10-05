import os
import json
from platform import system
from logger import log

IMAGE_SIZE = 2
BASE_URL = 'https://himawari8-dl.nict.go.jp/himawari8'
IMG_PATH = '/img/D531106/$sized/550/'
IMAGE_DIR = ''
CACHE_DIR = ''
OS = system()

home_dir = ''

if OS == 'Windows':
    home_dir = os.environ['USERPROFILE']
    CACHE_DIR = home_dir + '/AppData/Local/Temp/himawari8/'
elif OS == 'Linux':
    home_dir = os.environ['HOME']
    CACHE_DIR = '/tmp/himawari8/'

IMAGE_DIR = home_dir + '/.himawari8-images/'

if os.path.exists('./config.json'):
    config = json.load(open('./config.json'))
    custom_image_dir = config.get('image_dir')
    custom_size = config.get('size')

    if os.path.exists(custom_image_dir):
        log.info('Load custom image directory: %s.' % custom_image_dir)
        IMAGE_DIR = custom_image_dir
    try:
        size = int(custom_size)
        if (size in [2, 4, 8, 16, 20]):
            log.info('Load custom image size: %d.' % size)
            IMAGE_SIZE = size
    except Exception as e:
        log.error('Custom size invalid.')