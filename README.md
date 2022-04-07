<h1  align="center">Ashore</h1>

<img src="static/icon/icon.funtion/icon0.png" style="zoom:33%;" />

<p align="center"><br>Ashore 是一个用Python编写的内核为aria2的下载工具。<br><br></p>

&emsp;&emsp;![](https://img.shields.io/badge/python-v3.10-blue)&ensp;![](https://img.shields.io/badge/PyQt-v6-yellowgreen)&ensp;![PyPI - License](https://img.shields.io/badge/license-GPL-blue)&ensp;[![download](https://img.shields.io/badge/download-82M-brightgreen)](https://github.com/PanZK/videoSorter/releases)

---

## Origin

&emsp;下载器有很多，逐渐变得不好用，使用aria2后感觉很好，没有界面是一大特点，但用着也稍嫌费劲。市面上已有的界面又不太符合自己的要求，就用Python做了一个。

## Features

- 下载内核部分使用[aria2](https://github.com/aria2/aria2)
- 过渡部分使用[aria2p](https://github.com/pawamoy/aria2p)
- 程序界面使用[PyQt6](https://pypi.org/project/PyQt6/)制作
- 默认使用aria2的RPC端口号为 `6801`避免冲突
- 其他配置同aria2
- 关于aria2的配置[Mac下配置Aria2](https://gist.github.com/sumpeter/9f71b26b0e79cfd3bae39c3bdf6cfd8c)这里讲的非常细致
- 目前功能未完全实现，界面也没好好写

## Usage

1. 下载[release](https://github.com/PanZK/videoSorter/releases)中的 `dmg` 文件，打开后将Video Sorter拉进 `Applications` 文件夹，即可在程序坞中找到；
2. 打开运行Video Sorter，开始会选择视频所在文件夹(比如选择 `~/Downloads` )、视频归类整理文件夹(比如选择 `~/Moives` )；
3. 选择好正确目录后，程序会自动播放获取到的视频，并在右侧列表处列出目标目录的各文件夹，点击右侧列表进行分类；
4. 列表进入末级目录后便可自动生成相应终端中的 `mv` 命令，点击右侧列表上方的tab标签可切换查看目录结构或已生成命令；
5. 待所有视频遍历结束，或中途退出程序时，可选择将已生成命令现在执行，或保存为 `txt` 文件以便后续使用。

## Development

###  [videoSorter.py](https://github.com/PanZK/videoSorter/blob/main/videoSorter.py)为完整程序入口，其中包括：

- 1 [initialPathWidget.py](https://github.com/PanZK/videoSorter/blob/main/initialPathWidget.py)用来开始程序并初始化路径；

- 2 通过[initialPathWidget.py](https://github.com/PanZK/videoSorter/blob/main/initialPathWidget.py)得到的路径，建立[videoSorter.py](https://github.com/PanZK/videoSorter/blob/main/videoSorter.py)主程序，其中：
  - 2.1 [videoPlayerWidget.py](https://github.com/PanZK/videoSorter/blob/main/videoPlayerWidget.py)为使用[opencv-python](https://github.com/opencv/opencv-python)视频渲染部分；
  
  - 2.2 [obtainPaths.py](https://github.com/PanZK/videoSorter/blob/main/obtainPaths.py)为路径及文件名等操作部分；
  
- 3 [videoSorter.py](https://github.com/PanZK/videoSorter/blob/main/videoSorter.py)主程序完成或退出后，将命令保存列表交给[executeCmdWidget.py](https://github.com/PanZK/videoSorter/blob/main/executeCmdWidget.py)执行

---

<p align="center">
  Enjoy it!
</p>
