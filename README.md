<h1  align="center">Ashore</h1>

<p align="center">
  <a target="_blank" href="https://github.com/PanZK/Ashore"><img src="https://raw.githubusercontent.com/PanZK/Ashore/main/static/icon/icon.funtion/icon0.png"></a></p>
<p align="center"><br>Ashore 是一个用Python编写的内核为aria2的界面管理程序。<br><br>
</p>

&emsp;&emsp;![](https://img.shields.io/badge/python-v3.10-blue)&ensp;![](https://img.shields.io/badge/PyQt-v6-yellowgreen)&ensp;![PyPI - License](https://img.shields.io/badge/license-GPL-blue)&ensp;[![download](https://img.shields.io/badge/download-50M-brightgreen)](https://github.com/PanZK/Ashore/releases)

---

## Origin

&emsp;下载器有很多，逐渐变得不好用，使用aria2后感觉很好，没有界面是一大特点，但用着也稍嫌费劲。网络上已有很多大佬做的各种界面程序基本都使用过感觉都非常棒，不过有时候太符合自己操作习惯，在再加上自己想练练手，遂coding小白就用Python做了一个。

## Features

- 下载内核部分直接使用[aria2](https://github.com/aria2/aria2)
- 程序界面使用[PyQt6](https://pypi.org/project/PyQt6/)制作
- aria2的设置默认为localhost、RPC端口号为 `6801`避免冲突
- Ashore配置文件单独存放于ashore.conf文件中
- 程序中可对aria2的配置简单进行更改，后续可以加入更多配置选项（[Mac下配置Aria2](https://gist.github.com/sumpeter/9f71b26b0e79cfd3bae39c3bdf6cfd8c)这里讲的非常细致）

## Stand by

- Ubuntu 18.04 或更高版本
- MacOS 10.15 或更高版本

## Install

### 	MacOS

1. 确认已安装好[aria2](https://github.com/aria2/aria2)；
2. 下载[release](https://github.com/PanZK/videoSorter/releases)中的 `dmg` 文件；
3. 双击运行 `dmg` 文件，将Ashorer拉进 `Applications` 文件夹；
4. 程序坞中找到，点击运行。

### 	Linux

1. 确认已安装好[aria2](https://github.com/aria2/aria2)；

2. 下载Linux系统载[release](https://github.com/PanZK/videoSorter/releases)中的zip并解压；

3. 终端进入解压目录执行

   ```
   sudo chmod +x make.sh
   sudo ./make.sh
   ```

   赋予权限后运行

4. Ashore将会被安装在 `/opt/Ashore` 文件夹，同时应用程序列表中也会列出；

### 	Windows

- 尚未测试



## Usage

1. 运行Ashore后界面如下：

   

   <p align="center">
     <img src="https://raw.githubusercontent.com/PanZK/Ashore/main/static/icon/icon.funtion/surface.png"></p>

2. 程序图标为主，上手简单。

## make

1. 编程环境vscode、python3.10、pyqt6

2. clone项目后解压，终端进入解压目录执行

   ```
   sudo chmod +x make.py
   python3 make.py
   ```

   按提示操作

## Development

1. 上一版是通过[aria2p](https://github.com/pawamoy/aria2p)实现，后面感觉过于繁琐，故自行写了一版，目前仍有许多不足，后续继续努力；
2. 欠缺一套常用文件类型的系列图标；
3. 界面也没好好写，后续考虑加入深浅色配置并优化界面；
4. 对于rpcserver发送出来的消息不知如何获取，暨aria2在任务完成/出错等情况时发送的消息不知如何接收，后面想办法；
5. 目前手头没有Windows实体机及虚拟机，还未对win平台做测试；
6. 添加多语言选项；
7. 后续考虑对任务管理添加多选功能。



---

<p align="center">
  Enjoy it!
</p>
