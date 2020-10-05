import json
import os
import sys
import time
from shutil import rmtree

import requests

from earth_compose import compose
from env import BASE_URL, CACHE_DIR, IMAGE_DIR, IMG_PATH, OS
from logger import log

if OS == 'Windows':
    import win32.lib.win32con as win32con
    from win32 import win32api, win32gui

temp_dir = ''


def create_dir(path):
    '''
    创建临时文件夹

    Args:
        path: 保存图片每个区域的临时目录
    '''
    if not os.path.exists(path):
        os.makedirs(path)
        global temp_dir
    temp_dir = path


def get_latest_timestamp():
    '''
    根据当前时间从 himawari8 官网获取最新时间戳

    Returns:
        latest_timestamp: 来自 himawari8 的最新时间戳
    '''
    timestamp = round(time.time())
    log.info('Fetching Latest Timestamp.')
    url = BASE_URL + '/img/FULL_24h/latest.json?_=' + str(timestamp)
    req = requests.get(url)
    latest_timestamp = ''

    if (req.status_code == 200):
        latest_timestamp = json.loads(req.content).get('date')
        log.info('Latest Timestamp: %s.' % latest_timestamp)
        latest_timestamp = str(latest_timestamp).replace(
            '-', '/').replace(' ', '/').replace(':', '')

    del req
    return latest_timestamp


def get_earth_part(path, timestamp, x, y):
    '''
    获取每个部分的图片

    发送请求从 himawari8 api 获取图片

    Args:
        path: 请求 URL 的一部分
        timestamp: UNIX 时间戳
    '''
    file = '%d_%d.png' % (x, y)
    if not os.path.exists(temp_dir + '%03d_%03d.png' % (x, y)):
        url = BASE_URL + path + timestamp + '_' + file
        req = requests.get(url, stream=True)

        if req.status_code == 200:
            open(temp_dir + '%03d_%03d.png' % (x, y), 'wb+').write(req.content)
        del req


def get_earth_by_size(timestamp, size):
    '''
    根据时间戳和大小获取每个区域的图片

    Args:
        timestamp: 从 himawari8 api 获取的最新时间戳
        size: 取值范围为 [2, 4, 8, 16, 20], 图片分辨率为 (550 * size) ^ 2
    '''
    i, total = 1, size * size
    path = IMG_PATH.replace('$size', str(size))
    create_dir(CACHE_DIR + "%s/%dd/" % (timestamp, size))
    # 获取每个区域
    for y in range(0, size, 1):
        for x in range(0, size, 1):
            log.info('Getting Parts: %d/%d.' % (i, total))
            get_earth_part(path, timestamp, x, y)
            i = i + 1


def set_wallpaper_gnome(path):
    '''
    设置 Gnome 桌面环境的壁纸
    '''
    abs_path = os.path.abspath(path)
    os.system("gsettings set org.gnome.desktop.background primary-color '#000000'")
    os.system("gsettings set org.gnome.desktop.background picture-options 'scaled'")
    os.system(
        'gsettings set org.gnome.desktop.background picture-uri file://' + abs_path)
    log.info('Current Wallpaper: %s.' % abs_path)


def set_wallpaper_windows(path):
    '''调用 win32 api 设置桌面壁纸
    '''
    BACKGROUND_COLOR = win32api.RGB(0, 0, 0)
    win32api.SetSysColors((win32con.COLOR_DESKTOP,), (BACKGROUND_COLOR,))
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
    log.info('Current Wallpaper: %s.' % abs_path)


def set_wallpaper(path):
    if OS == 'Windows':
        set_wallpaper_windows(path)
    elif OS == 'Linux':
        set_wallpaper_gnome(path)


def del_old_images():
    '''
    删除旧图片

    30 分钟以前的图片将被删除
    '''
    images = os.listdir(IMAGE_DIR)
    for file_name in images:
        path = os.path.join(IMAGE_DIR, file_name)
        if (os.path.isfile(path)):
            ctime = os.path.getctime(path)
            t = (time.time() - ctime) / 60
            if (t > 30):
                os.remove(path)


def get_earth(size):
    if size in [2, 4, 8, 16, 20]:
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
        del_old_images()
    else:
        log.error('Invalid size: %d.' % size)
