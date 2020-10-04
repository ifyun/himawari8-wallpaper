import json
import os
import sys
import time
from shutil import rmtree

import requests
import win32.lib.win32con as win32con
from win32 import win32api, win32gui

from earth_compose import compose
from env import BASE_URL, IMG_PATH, IMAGE_DIR, CACHE_DIR

temp_dir = ''


# 创建临时文件夹
def create_dir(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        global temp_dir
    temp_dir = file_path


# 从 himawari8 官网获取最新时间戳
def get_latest_timestamp():
    timestamp = round(time.time())
    print('\033[0;30;43m Fetching Latest Timestamp... \033[0m')
    url = BASE_URL + '/img/FULL_24h/latest.json?_=' + str(timestamp)
    req = requests.get(url)
    latest_timestamp = ''
    if (req.status_code == 200):
        latest_timestamp = json.loads(req.content).get('date')
        print('\033[0;30;42m Latest Timestamp: %s \033[0m' % latest_timestamp)
        latest_timestamp = str(latest_timestamp).replace(
            '-', '/').replace(' ', '/').replace(':', '')
    del req
    return latest_timestamp


# 获取每个部分的图片
def get_earth_part(path, timestamp, x, y):
    file = '%d_%d.png' % (x, y)
    if not os.path.exists(temp_dir + '%03d_%03d.png' % (x, y)):
        url = BASE_URL + path + timestamp + '_' + file
        req = requests.get(url, stream=True)

        if req.status_code == 200:
            open(temp_dir + '%03d_%03d.png' % (x, y), 'wb+').write(req.content)
        del req


def get_earth_by_size(timestamp, size):
    i, total = 1, size * size
    if size in [2, 4, 8, 16, 20]:
        path = IMG_PATH.replace('$size', str(size))
        create_dir(CACHE_DIR + "%s/%dd/" % (timestamp, size))
        # 获取每个区域
        for y in range(0, size, 1):
            for x in range(0, size, 1):
                print('\033[0;30;43m Getting Parts: %d/%d \r\033[0m' %
                      (i, total), end='')
                get_earth_part(path, timestamp, x, y)
                i = i + 1
    else:
        sys.stderr.write('\033[0;30;41m Invalid size: %d \033[0m' % size)


# 设置桌面背景色为黑色
def set_background_color():
    BACKGROUND_COLOR = win32api.RGB(0, 0, 0)
    win32api.SetSysColors((win32con.COLOR_DESKTOP,), (BACKGROUND_COLOR,))


# 调用 win32 api 设置桌面壁纸
def set_wallpaper(path):
    set_background_color()
    abs_path = os.path.abspath(path)
    reg_key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER,
                                    'Control Panel\\Desktop',
                                    0,
                                    win32con.KEY_SET_VALUE)
    win32api.RegSetValueEx(reg_key, "WallpaperStyle", 0, win32con.REG_SZ, "6")
    win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER,
                                  abs_path,
                                  win32con.SPIF_SENDWININICHANGE)
    win32api.RegCloseKey(reg_key)
    print('\033[0;30;42m Current Wallpaper: %s \033[0m' % abs_path)


def get_earth(size):
    time = get_latest_timestamp()
    filename = time.replace('/', '-')
    earth_path = IMAGE_DIR + '%s.png' % filename
    # 如果本地图片已经是最新就不从服务器获取
    if not os.path.exists(earth_path):
        if time != '':
            get_earth_by_size(time, size)
            compose(temp_dir, size, filename)
            rmtree(CACHE_DIR)
    set_wallpaper(earth_path)
