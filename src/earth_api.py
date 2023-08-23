import json
import os
import time

import cv2
import requests
import urllib.request
import numpy as np
from cv2 import BORDER_CONSTANT, copyMakeBorder, imwrite
from src.env import ENV, LOG

if ENV.OS == 'Windows':
    import win32.lib.win32con as win32con
    import win32api
    import win32gui


class Earth:
    _parts = []
    _count = pow(ENV.IMAGE_SIZE, 2)

    def get(self, size):
        if size in [2, 4, 8, 16, 20]:
            _time = self._get_latest_timestamp()
            filename = _time.replace('/', '-')
            earth_path = ENV.IMAGE_DIR + '%s.jpg' % filename
            # 如果本地图片已经是最新就不从服务器获取
            if not os.path.exists(earth_path):
                if _time != '':
                    self._get_earth_by_size(_time, size)
                    self._compose(filename, size)
            _set_wallpaper(earth_path)
            _del_old_images(ENV.DEL_BEFORE)
        else:
            LOG.error('Invalid size: %d' % size)

    @staticmethod
    def _get_latest_timestamp():
        """
        根据当前时间从 himawari8 官网获取最新时间戳

        Returns:
            latest_timestamp: 来自 himawari8 的最新时间戳
        """
        timestamp = round(time.time())
        url = ENV.BASE_URL + '/img/FULL_24h/latest.json?_=' + str(timestamp)
        req = requests.get(url)
        latest_timestamp = ''

        if req.status_code == 200:
            latest_timestamp = json.loads(req.content).get('date')
            LOG.info('Latest Timestamp: %s' % latest_timestamp)
            latest_timestamp = str(latest_timestamp).replace('-', '/').replace(' ', '/').replace(':', '')

        del req
        return latest_timestamp

    def _get_earth_part(self, path, timestamp, x, y):
        """
        获取每个部分的图片

        发送请求从 himawari8 api 获取图片

        Args:
            path: 请求 URL 的一部分
            timestamp: UNIX 时间戳
            x: 图片区域的横坐标
            y: 图片区域的纵坐标
        """
        file = '%d_%d.png' % (x, y)
        url = ENV.BASE_URL + path + timestamp + '_' + file
        res = urllib.request.urlopen(url)
        img = np.asarray(bytearray(res.read()), dtype="uint8")
        self._parts.append(cv2.imdecode(img, cv2.IMREAD_COLOR))
        del res

    def _get_earth_by_size(self, timestamp, size):
        """
        根据时间戳和大小获取每个区域的图片

        Args:
            timestamp: 从 himawari8 api 获取的最新时间戳
            size: 取值范围为 [2, 4, 8, 16, 20], 图片分辨率为 (550 * size) ^ 2
        """
        self._parts = []
        i, total = 1, size * size
        path = ENV.IMG_PATH.replace('$size', str(size))
        # 获取每个区域
        for x in range(0, size, 1):
            for y in range(0, size, 1):
                LOG.info('Getting Earth: %d/%d' % (i, total))
                self._get_earth_part(path, timestamp, x, y)
                i = i + 1

    def _compose(self, filename, size):
        """
        拼接图片

        Args:
            filename: 文件名
        """
        LOG.info('Composing Earth Image')

        if not os.path.exists(ENV.IMAGE_DIR):
            os.mkdir(ENV.IMAGE_DIR)
        if len(self._parts) != self._count:
            return
        earth_parts = []
        '''
        如果存在纯黑色区域，那么这张图是二维矩阵，需要筛选出来处理
        '''
        for i in range(0, len(self._parts)):
            if np.ndim(self._parts[i]) == 2:
                t = np.full((550, 550, 3), 0)
                self._parts[i] = t
        for i in range(0, pow(size, 2), size):
            earth_parts.append(np.concatenate(self._parts[i:i + size], 0))

        data = np.concatenate(earth_parts, 1)
        earth_file_path = ENV.IMAGE_DIR + '%s.jpg' % filename
        self._save(data, earth_file_path)
        del earth_parts

    @staticmethod
    def _save(data, earth_path):
        """
        四周加黑边保存

        Args:
            data: 拼接后的图片矩阵
            earth_path: 加黑边后的保存路径
        """
        black = [0, 0, 0]
        img = copyMakeBorder(data, 300, 300, 300, 300, BORDER_CONSTANT, value=black)
        imwrite(earth_path, img)
        del img


def _set_wallpaper_gnome(path):
    """
    设置 Gnome 桌面环境的壁纸
    """
    abs_path = os.path.abspath(path)
    os.system("gsettings set org.gnome.desktop.background primary-color '#000000'")
    os.system("gsettings set org.gnome.desktop.background picture-options 'scaled'")
    os.system('gsettings set org.gnome.desktop.background picture-uri file://' + abs_path)
    # 暗色模式需要使用 picture-uri-dark
    os.system('gsettings set org.gnome.desktop.background picture-uri-dark file://' + abs_path)
    LOG.info('Current Wallpaper: %s' % abs_path)


def _set_wallpaper_windows(path):
    """
    调用 win32 api 设置桌面壁纸
    """
    back_color = win32api.RGB(0, 0, 0)
    win32api.SetSysColors((win32con.COLOR_DESKTOP,), (back_color,))
    abs_path = os.path.abspath(path)
    reg_key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, 'Control Panel\\Desktop', 0, win32con.KEY_SET_VALUE)
    win32api.RegSetValueEx(reg_key, "WallpaperStyle", 0, win32con.REG_SZ, "6")
    win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, abs_path, win32con.SPIF_SENDWININICHANGE)
    win32api.RegCloseKey(reg_key)
    LOG.info('Current Wallpaper: %s' % abs_path)


def _set_wallpaper(path):
    if ENV.OS == 'Windows':
        _set_wallpaper_windows(path)
    elif ENV.OS == 'Linux':
        _set_wallpaper_gnome(path)


def _del_old_images(before):
    """
    删除旧图片

    before 分钟以前的图片将被删除
    """
    if before <= 0:
        return
    images = os.listdir(ENV.IMAGE_DIR)
    for file_name in images:
        path = os.path.join(ENV.IMAGE_DIR, file_name)
        if os.path.isfile(path):
            ctime = os.path.getctime(path)
            t = (time.time() - ctime) / 60
            if t > before:
                os.remove(path)


earth = Earth()
