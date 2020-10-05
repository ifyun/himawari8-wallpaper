import glob
import os
import sys

import numpy as np
from cv2 import BORDER_CONSTANT, copyMakeBorder, imread, imwrite

from env import IMAGE_DIR
from logger import log


def compose(img_dir, size, timestamp):
    '''
    拼接图片

    Args:
        img_dir: 存放图片各个区域的目录
        size: 图片大小，表示由 size ^ 2 张图片拼接
        timestamp: 时间，作为文件名
    '''
    log.info('Composing Earth Image.')
    images = []

    if not os.path.exists(IMAGE_DIR):
        os.mkdir(IMAGE_DIR)

    for file in sorted(glob.glob(img_dir + '0*.png')):
        img = imread(file, -1)
        images.append(img)

    if len(images) > 0:
        earth_parts = []
        '''
        Himawari8 官方的图片中，如果存在纯黑色区域，
        那么这张图是二维矩阵，需要筛选出来处理
        '''
        for i in range(0, len(images)):
            if np.ndim(images[i]) == 2:
                t = np.full((550, 550, 3), 0)
                images[i] = t
        for i in range(0, pow(size, 2), size):
            earth_parts.append(np.concatenate(images[i:i + size], 0))

        earth = np.concatenate(earth_parts, 1)
        earth_file_path = IMAGE_DIR + '%s.png' % timestamp
        add_padding(earth, earth_file_path)
    else:
        sys.stderr.write('No images!')
    del earth_parts
    del images


def add_padding(earth, earth_path):
    '''
    四周加黑边保存

    Args:
        earth: 拼接后的图片矩阵
        earth_path: 加黑边后的保存路径
    '''
    BLACK = [0, 0, 0]
    img = copyMakeBorder(earth, 200, 200, 200, 200,
                         BORDER_CONSTANT, value=BLACK)
    imwrite(earth_path, img)
    del img
