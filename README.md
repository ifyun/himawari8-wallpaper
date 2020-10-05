# 向日葵8号实时地球桌面

此程序自动从 Himawari8 官方 API 获取最新的地球卫星图设置为桌面。

支持的平台：

- Windows
- Linux(Gnome Desktop Only)

![Preview](./assets/preview.jpg)

## 使用方法

首先安装 Python 3.8，然后安装 `pipenv`：

```bash
pip install pipenv
```

> 提示：Windows 安装 `pipenv` 后需要设置环境变量才能使用，Linux 注销再登入即可使用。

### 1. 直接运行

执行根目录下的 `run.sh`：

```bash
pipenv install && sh ./run.sh
```

### 2. 生成可执行文件

执行根目录下的 `build.sh`：

```bash
pipenv install && sh ./build.sh
```

> 在 Linux 环境下会提示 `pypiwin32` 无法安装，忽略即可。

- 生成的可执行文件在 `dist` 目录下，没有图形界面
- 每 5 分钟更新一次（本地已存在最新图片不会发送请求），官方的更新间隔是从整点开始，每 10 分钟一次
- 获取的地球图片默认保存在 `~\.himawari8-images` 目录下（只保留 30 分钟以内的图片），可以在 `config.json` 中自定义

Windows 执行 exe 文件会自动进入后台运行，Linux 系统可使用 `nohup`：

```bash
nohup ./himawari8 >/dev/null 2>&1 &
```

`config.json` 文件中的 `size` 属性可以指定地球的大小，取值为 [2, 4, 8, 16, 20]，表示获取的地球图片由 size ^ 2 张图片组成，每张的分辨率为 550 * 550，可以根据需要修改，默认为 2。

不同取值对应的分辨率如下：

- size = 2：1100 * 1100
- size = 4：2200 * 2200
- size = 8：4400 * 4400
- size = 16：8800 * 8800
- size = 20：11000 * 11000

> 提示： 当分辨率为 11000 * 11000 时，文件会达到 100MB。