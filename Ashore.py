#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2022/03/20 20:12:13
@File    :   Ashore.1.py
@Software:   VSCode
@Author  :   PPPPAN 
@Version :   1.0
@Contact :   for_freedom_x64@live.com
'''

import sys, os, subprocess, time
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedLayout, QListWidget, QMessageBox, QFileDialog, QProgressBar, QFrame, QScrollArea, QDialog, QTextEdit, QLineEdit, QGridLayout, QSplashScreen
from PyQt6.QtGui import QGuiApplication, QFont, QIcon, QImage,QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QTimer, QSize
from section import Section
from page import Page
from aria2Operate import Aria2Operate
from addNewDialog import AddNewDialog
from settingPage import SettingPage

DEFAULTPATH = os.path.expanduser('~/Downloads')

class Ashore(QMainWindow):
    def __init__(self):
        super().__init__()
        self.downloadingList = []
        self.aria2Operate = Aria2Operate()
        # self.aria2ConfPath = self.aria2Operate.getConfigPath()
        self.initUI()
        self.setConnect()
        self.updatePage()
        self.timer = QTimer(self)  # 初始化一个定时器
        self.timer.timeout.connect(self.updatePage)  # 每次计时到时间时发出信号
        self.timer.start(1000)  # 设置计时间隔并启动；单位毫秒

    def initUI(self):
        self.tabDownloading = QPushButton(QIcon('static/icon/icon.funtion/download.png'),'')
        self.tabDownloading.setFlat(True)
        self.tabDownloading.setIconSize(QSize(23,23))
        self.tabDownloading.setToolTip('下载中')
        self.tabDownloaded = QPushButton(QIcon('static/icon/icon.funtion/complete.png'),'')
        self.tabDownloaded.setFlat(True)
        self.tabDownloaded.setIconSize(QSize(23,23))
        self.tabDownloaded.setToolTip('已完成')
        self.tabSetting = QPushButton(QIcon('static/icon/icon.funtion/setting.png'),'')
        self.tabSetting.setFlat(True)
        self.tabSetting.setIconSize(QSize(23,23))
        self.tabSetting.setToolTip('设置')
        tabLayout = QVBoxLayout()
        tabLayout.addWidget(self.tabDownloading)
        tabLayout.addWidget(self.tabDownloaded)
        tabLayout.addStretch(10)
        tabLayout.addWidget(self.tabSetting)
        self.addBtn = QPushButton(QIcon('static/icon/icon.funtion/add.png'),'')
        self.addBtn.setFlat(True)
        self.addBtn.setIconSize(QSize(20,20))
        self.addBtn.setToolTip('新建下载')
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
        self.setWindowIcon(QIcon('static/icon/icon.funtion/icon.png'))
        self.setStyleSheet('''
            Ashore QPushButton{width:40;height:40;border-radius:8;}
            Ashore QPushButton:hover{background-color:#5f5f5f;border: 1 solid #bababa;}
            Ashore QPushButton:pressed{background-color:#363636;border: 1 solid #919191;}
            Ashore Section QPushButton{width:23;height:23;border-radius:3;}
            SettingPage QPushButton{width:23;height:23;border-radius:3;background-color:#5d795f}
        ''')
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
        self.pageStack.setCurrentIndex(0)
    def slotSwitchDownloaded(self):
        self.pageStack.setCurrentIndex(1)

    def slotSwitchSetting(self):
        options = self.aria2Operate.getGlobalConfig()
        self.pageSetting.updateSetting(options)
        self.pageStack.setCurrentIndex(2)

    def slotAddNew(self):
        form = AddNewDialog(DEFAULTPATH)
        form.sinOut.connect(self.slotUrlsPath)
        form.show()
        form.exec()
        self.updatePage()

    def slotUrlsPath(self, data):
        urls = data[0]
        path = data[1]
        if len(urls) == 1:
            #单文件
            self.aria2Operate.addDownload(urls[0], path)
        else:
            #多文件
            self.aria2Operate.addDownloads(urls, path)

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
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('static/icon/icon.funtion/icon.png'))
    app.setApplicationVersion('0.0.75')
    splash = QSplashScreen(QPixmap(r"static/img/cover.png"))
    splash.show()                               #展示启动图片
    app.processEvents()                         #防止进程卡死
    exe = Ashore()
    exe.show()
    splash.finish(exe)                  #关闭启动界面
    sys.exit(app.exec())