import os
import json
import logging
from logging.handlers import RotatingFileHandler
from platform import system

global LOG


class Env:
    OS = system()
    IMAGE_SIZE = 4
    DEL_BEFORE = 0
    BASE_URL = 'https://himawari8-dl.nict.go.jp/himawari8'
    IMG_PATH = '/img/D531106/$sized/550/'
    IMAGE_DIR = ''

    def __init__(self):
        home_dir = ''
        if self.OS == 'Windows':
            home_dir = os.environ['USERPROFILE']
        elif self.OS == 'Linux':
            home_dir = os.environ['HOME']

        self.IMAGE_DIR = home_dir + '/.himawari8/'

        global LOG
        LOG = logging.getLogger()
        LOG.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        file_handler = RotatingFileHandler(home_dir + '/himawari8.log', 'w', 1024000, 2, 'utf-8')
        file_handler.setLevel(logging.INFO)

        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        LOG.addHandler(console_handler)
        LOG.addHandler(file_handler)

        if os.path.exists(home_dir + '/himawari8.json'):
            config = json.load(open(home_dir + '/himawari8.json'))
            custom_image_dir = config.get('image_dir')
            custom_size = config.get('size')
            del_time = config.get('del_before')

            LOG.info('Load image_dir: %s' % custom_image_dir)
            if custom_image_dir != '':
                self.IMAGE_DIR = custom_image_dir
                if not os.path.exists(self.IMAGE_DIR):
                    os.mkdir(self.IMAGE_DIR)

            try:
                size = int(custom_size)
                if size in [2, 4, 8, 16, 20]:
                    LOG.info('Load size: %d' % size)
                    self.IMAGE_SIZE = size
                self.DEL_BEFORE = int(del_time)
            except ValueError:
                LOG.error('Invalid config value')
        else:
            config = {
                "cache_dir": "",
                "image_dir": "",
                "size": 4,
                "del_before": 0
            }

            with open(home_dir + '/himawari8.json', 'w') as file:
                json.dump(config, file, indent=4)


ENV = Env()
