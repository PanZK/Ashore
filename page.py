#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2022/03/20 22:41:51
@File    :   page.py
@Software:   VSCode
@Author  :   PPPPAN 
@Version :   1.0
@Contact :   for_freedom_x64@live.com
'''

import sys, os
from PyQt6.QtWidgets import QApplication, QTabWidget, QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedLayout, QListWidget, QMessageBox, QFileDialog, QProgressBar, QFrame, QScrollArea
from PyQt6.QtGui import QGuiApplication, QFont, QIcon, QImage,QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QRect
from section import Section

class Page(QScrollArea):
    def __init__(self):
        super().__init__()
        self.sectionsDic = {}
        self.initUI()
    
    def initUI(self):
        self.sectionLayout = QVBoxLayout()
        self.sectionLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.sectionLayout.setSpacing(10)
        self.sectionListWidget = QWidget()
        self.sectionListWidget.setLayout(self.sectionLayout)
        self.sectionListWidget.setMinimumSize(815,50)
        self.sectionListWidget.adjustSize()
        self.setWidget(self.sectionListWidget)
        self.setMinimumSize(830, 400)

    def resizeEvent(self,event):
        self.sectionListWidget.resize(event.size().width()-5,self.sectionListWidget.height())
        self.update()
    
    def updateSections(self, files):    #刷新界面
        tempList = []
        w = self.sectionListWidget.width()
        for file in files:
            if self.sectionsDic.get(file.gid) == None:
                #不在已有列表中，新建实例并添加进布局
                self.sectionsDic.update({file.gid : Section(gid=file.gid, fileName=file.name, status=file.status, fileSize=file.total_length, completedSize=file.completed_length, speed=file.download_speed)})
                self.sectionLayout.addWidget(self.sectionsDic[file.gid])
                h = self.sectionListWidget.height()
                self.sectionListWidget.resize(w, h+120)
            else:
                #在已有列表中，更新信息
                self.sectionsDic[file.gid].updateInfo(status=file.status, fileSize=file.total_length, completedSize=file.completed_length, speed=file.download_speed)
            tempList.append(file.gid)
        #把不在列表内的删除
        for gid,item in list(self.sectionsDic.items()):
            if gid not in tempList:
                self.sectionLayout.removeWidget(item)
                self.sectionsDic.pop(gid, '删除失败')
                h = self.sectionListWidget.height()
                self.sectionListWidget.resize(w, h-120)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    exe = Page()
    exe.show()
    sys.exit(app.exec())