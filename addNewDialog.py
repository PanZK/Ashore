#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2022/03/25 15:06:43
@File    :   addNew.py
@Software:   VSCode
@Author  :   PPPPAN 
@Version :   1.0
@Contact :   for_freedom_x64@live.com
'''

import sys, os, re
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedLayout, QListWidget, QMessageBox, QFileDialog, QProgressBar, QFrame, QScrollArea, QDialog, QTextEdit, QLineEdit, QGridLayout
from PyQt6.QtCore import Qt, pyqtSignal

REDIC = {
    'url' : r'(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?',
    'bt' : r'/^(magnet:\?xt=urn:btih:)[0-9a-fA-F]{40}.*$/'
    }

class AddNewDialog(QDialog):

    sinOut = pyqtSignal(tuple)

    def __init__(self, downloadPath):
        super().__init__()
        self.downloadPath = downloadPath
        self.text = QTextEdit()
        self.text.setPlaceholderText("请输入下载地址,多个地址请用enter分割")
        self.dirEdit = QLineEdit(self.downloadPath)
        dirBtn = QPushButton('选择目录')
        dirBtn.setFixedWidth(100)
        confirmBtn = QPushButton('确认')
        confirmBtn.setFixedWidth(100)
        cancelBtn = QPushButton('取消')
        cancelBtn.setFixedWidth(100)
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.text, 0, 0, 1, 7)
        mainLayout.addWidget(self.dirEdit, 1, 0, 1, 6)
        mainLayout.addWidget(dirBtn, 1, 6, 1, 1)
        mainLayout.addWidget(confirmBtn, 2, 2, 1, 1)
        mainLayout.addWidget(cancelBtn, 2, 4, 1, 1)
        mainLayout.setColumnMinimumWidth(0,100)
        self.setLayout(mainLayout)
        self.setMinimumSize(500, 300)
        self.setWindowModality(Qt.WindowModality.NonModal)  # 非模态，可与其他窗口交互
        dirBtn.clicked.connect(self.slotDir)
        confirmBtn.clicked.connect(self.slotConfirm)
        cancelBtn.clicked.connect(self.close)

    def slotDir(self):
        path = QFileDialog.getExistingDirectory(self,'Open dir', self.downloadPath, QFileDialog.Option.ShowDirsOnly)
        if path != '':
            self.dirEdit.setText(path)

    def slotConfirm(self):
        text = self.text.toPlainText()
        if text != '':
            urlList = []
            #校验是否为url或bt
            for item in text.split('\n'):
                temp1 = re.findall(REDIC['url'], item)
                temp2 = re.findall(REDIC['bt'], item)
                if temp1 != [] or temp2 != []:
                    urlList.append(item)
            dir = self.dirEdit.text()
            self.sinOut.emit((urlList,dir))
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    exe = AddNewDialog()
    exe.show()
    sys.exit(app.exec())