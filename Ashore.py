#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2022/03/20 20:12:13
@File    :   Ashore.py
@Software:   VSCode
@Author  :   PPPPAN 
@Version :   0.1.75
@Contact :   for_freedom_x64@live.com
'''

import sys, os, subprocess
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedLayout, QSplashScreen, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QAction
from PyQt6.QtCore import QTimer, QSize
from page import Page
from aria2Operate import Aria2Operate
from addNewDialog import AddNewDialog
from settingPage import SettingPage

DEFAULTPATH = os.path.expanduser('~/Downloads')

class Ashore(QMainWindow):
    def __init__(self):
        super().__init__()
        #生成资源文件目录访问路径
        #说明： pyinstaller工具打包的可执行文件，运行时sys。frozen会被设置成True
        #      因此可以通过sys.frozen的值区分是开发环境还是打包后的生成环境
        #
        #      打包后的生产环境，资源文件都放在sys._MEIPASS目录下
        #      修改main.spec中的datas，
        #      如datas=[('res', 'res')]，意思是当前目录下的res目录加入目标exe中，在运行时放在零时文件的根目录下，名称为res
        self.BASEPATH = ''
        if getattr(sys, 'frozen', False):
            self.BASEPATH = sys._MEIPASS + '/'
        # print(os.path.abspath(__file__))
        # print(cur_path)
        # print(sys.executable)
        self.downloadingList = []
        self.aria2Operate = Aria2Operate()
        # self.aria2ConfPath = self.aria2Operate.getConfigPath()
        self.initUI()
        self.setConnect()
        self.updatePage()
        self.timer = QTimer(self)  # 初始化一个定时器
        self.timer.timeout.connect(self.updatePage)  # 每次计时到时间时发出信号
        self.timer.start(1000)  # 设置计时间隔并启动；单位毫秒
    
    def createMenuBar(self):
        menuBar = self.menuBar()
        newBtn = QAction('新建下载',self)
        newBtn.setShortcut('Ctrl+N')
        newBtn.triggered.connect(self.slotAddNew)
        fileMenu = menuBar.addMenu("文件")
        fileMenu.addAction(newBtn)
        showBtn = QAction('显示窗口',self)
        showBtn.setShortcut('Ctrl+R')
        showBtn.triggered.connect(self.show)
        hideBtn = QAction('关闭窗口',self)
        hideBtn.setStatusTip('退出当前应用')
        hideBtn.setShortcut('Ctrl+W')
        hideBtn.triggered.connect(self.hide)
        windowMenu = menuBar.addMenu("窗口")
        windowMenu.addAction(showBtn)
        windowMenu.addAction(hideBtn)
        aboutBtn = QAction('关于',self)
        helpMenu = menuBar.addMenu("帮助")
        helpMenu.addAction(aboutBtn)
        self.setMenuBar(menuBar)

    def initUI(self):
        self.tabDownloading = QPushButton(QIcon(self.BASEPATH + 'static/icon/icon.funtion/download.png'),'')
        self.tabDownloading.setFlat(True)
        self.tabDownloading.setIconSize(QSize(23,23))
        self.tabDownloading.setToolTip('下载中')
        self.tabDownloading.setEnabled(False)
        self.tabDownloaded = QPushButton(QIcon(self.BASEPATH + 'static/icon/icon.funtion/complete.png'),'')
        self.tabDownloaded.setFlat(True)
        self.tabDownloaded.setIconSize(QSize(23,23))
        self.tabDownloaded.setToolTip('已完成')
        self.tabSetting = QPushButton(QIcon(self.BASEPATH + 'static/icon/icon.funtion/setting.png'),'')
        self.tabSetting.setFlat(True)
        self.tabSetting.setIconSize(QSize(23,23))
        self.tabSetting.setToolTip('设置')
        self.tabSetting.setShortcut("Ctrl+,")
        tabLayout = QVBoxLayout()
        tabLayout.addWidget(self.tabDownloading)
        tabLayout.addWidget(self.tabDownloaded)
        tabLayout.addStretch(10)
        tabLayout.addWidget(self.tabSetting)
        self.addBtn = QPushButton(QIcon(self.BASEPATH + 'static/icon/icon.funtion/add.png'),'')
        self.addBtn.setFlat(True)
        self.addBtn.setIconSize(QSize(20,20))
        self.addBtn.setToolTip('新建下载')
        self.addBtn.setShortcut("Ctrl+N")
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.addBtn)
        #添加弹簧
        btnLayout.addStretch(10)
        self.pageDownloading = Page()
        self.pageDownloaded = Page()
        self.pageSetting = SettingPage()
        self.pageStack = QStackedLayout()
        self.pageStack.addWidget(self.pageDownloading)
        self.pageStack.addWidget(self.pageDownloaded)
        self.pageStack.addWidget(self.pageSetting)
        pageLayout = QVBoxLayout()
        pageLayout.addLayout(btnLayout)
        pageLayout.addLayout(self.pageStack)
        mainLayout = QHBoxLayout()
        mainLayout.addLayout(tabLayout)
        mainLayout.addLayout(pageLayout)
        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)
        # self.mainLayout.setMinimumSize(1000,500)
        self.setMinimumSize(950,520)
        self.status = self.statusBar()
        #将提示信息显示在状态栏中showMessage（‘提示信息’，显示时间（单位毫秒））
        self.status.showMessage('这是状态栏提示',4000)
        #创建窗口标题
        self.setWindowTitle('Ashore')
        self.setWindowIcon(QIcon(self.BASEPATH + 'static/icon/icon.funtion/icon.png'))
        self.setStyleSheet('''
            Ashore QPushButton{width:40;height:40;border-radius:8;}
            Ashore QPushButton:hover{background-color:#5f5f5f;border: 1 solid #bababa;}
            Ashore QPushButton:pressed{background-color:#363636;border: 1 solid #919191;}
            Ashore Section QPushButton{width:23;height:23;border-radius:3;}
            SettingPage QPushButton{width:23;height:23;border-radius:3;background-color:#5d795f}
        ''')
        self.createMenuBar()

    def setConnect(self):
        self.addBtn.clicked.connect(self.slotAddNew)
        self.tabDownloading.clicked.connect(self.slotSwitchDownloading)
        self.tabDownloaded.clicked.connect(self.slotSwitchDownloaded)
        self.tabSetting.clicked.connect(self.slotSwitchSetting)
        self.pageSetting.sinOut.connect(self.slotSaveConfig)
        # self.pageDownloading.Section
        # self.Section.doubleClickOut.connect(self.slotDoubleClick)

    def updatePage(self):
        speed = 0
        aria2List = self.aria2Operate.getDownloading()
        #将所有下载文件按类型整理
        downloadFiles = {'active' : [], 'waiting' : [], 'paused' : [], 'complete' : [], 'error' : []}
        for item in aria2List:
            downloadFiles[item.status].append(item)
            if item.status == 'active':
                speed += item.download_speed
        self.pageDownloading.updateSections(downloadFiles['active'] + downloadFiles['waiting'] + downloadFiles['paused'])
        self.pageDownloaded.updateSections(downloadFiles['complete'] + downloadFiles['error'])
        self.status.showMessage(self.getSpeedStr(speed))
        self.setConnectByDic()

    def setConnectByDic(self):
        for item in self.pageDownloading.sectionsDic.values():
            item.disconnect()
            # 双击section和点击section中开始/暂停按钮效果同步
            item.doubleClickOut.connect(self.slotDoubleClick)
            item.openDirOut.connect(self.slotOpenFolder)
            item.removeDelOut.connect(self.slotRemoveDel)
        for item in self.pageDownloaded.sectionsDic.values():
            item.disconnect()
            # 双击section和点击section中开始/暂停按钮效果同步
            item.doubleClickOut.connect(self.slotDoubleClick)
            item.openDirOut.connect(self.slotOpenFolder)
            item.removeDelOut.connect(self.slotRemoveDel)

    def bytesInt2Str(self, b:int) -> str:
        if b < 1024:
            s = str(b) + 'B'
        elif b < 1048576:
            s = '{:.2f}KB'.format(b/1024)
        elif b < 1073741824:
            s = '{:.2f}MB'.format(b/1048576)
        elif b < 1099511627776:
            s = '{:.2f}GB'.format(b/1073741824)
        return s

    def getSpeedStr(self, speed:int) -> str:
        s = self.bytesInt2Str(speed) + '/s'
        return s

    def slotSwitchDownloading(self):
        self.tabDownloading.setEnabled(False)
        self.tabDownloaded.setEnabled(True)
        self.tabSetting.setEnabled(True)
        self.pageStack.setCurrentIndex(0)

    def slotSwitchDownloaded(self):
        self.tabDownloading.setEnabled(True)
        self.tabDownloaded.setEnabled(False)
        self.tabSetting.setEnabled(True)
        self.pageStack.setCurrentIndex(1)

    def slotSwitchSetting(self):
        self.tabDownloading.setEnabled(True)
        self.tabDownloaded.setEnabled(True)
        self.tabSetting.setEnabled(False)
        options = self.aria2Operate.getGlobalConfig()
        self.pageSetting.updateSetting(options)
        self.pageStack.setCurrentIndex(2)

    def slotAddNew(self):
        # form = AddNewDialog(DEFAULTPATH)
        form = AddNewDialog(self.pageSetting.getDownloadPath())
        form.sinOut.connect(self.aria2Operate.addDownloads)
        form.show()
        form.exec()
        self.updatePage()

    def slotDoubleClick(self, data:tuple):
        gid = data[0]
        status = data[1]
        #根据section状态判定双击的作用是开始或暂停
        if status == 'active' or status == 'waiting' :
            self.aria2Operate.pauseDownloads([gid])
        elif status == 'paused':
            self.aria2Operate.resumeDownloads([gid])
        elif status == 'complete':
            filePath = self.aria2Operate.getFilePath(gid)
            subprocess.run(['open', filePath])
        elif status == 'error':
            self.aria2Operate.retryDownloads([gid])
        self.updatePage()

    def slotOpenFolder(self, gid:str):
        dir = self.aria2Operate.getDir(gid)
        subprocess.run(['open',dir])
        self.updatePage()
    
    def slotRemoveDel(self, data:tuple):
        gid = data[0]
        cleanFiles = data[1]
        self.aria2Operate.removeDelDownloads([gid], delFiles=cleanFiles)
    
    def slotSaveConfig(self, conf:dict):
        self.aria2Operate.setGlobalConfig(conf)

if __name__ == '__main__':
    BASEPATH = ''
    if getattr(sys, 'frozen', False):
        BASEPATH = sys._MEIPASS + '/'
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)    #设置关闭窗口后最小化
    app.setWindowIcon(QIcon(BASEPATH + 'static/icon/icon.funtion/icon.icns'))
    splash = QSplashScreen(QPixmap(BASEPATH + 'static/img/cover.png'))
    splash.show()                               #展示启动图片
    app.processEvents()                         #防止进程卡死
    app.setApplicationVersion('0.0.75')
    app.setOrganizationName('PanZK')
    app.setApplicationName("Ashore")
    exe = Ashore()
    exe.show()
    splash.finish(exe)                  #关闭启动界面
    sys.exit(app.exec())