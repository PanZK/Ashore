#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/03/25 15:06:43
@File    :   addNewDialog.py
@Software:   VSCode
@Author  :   PPPPAN 
@Version :   0.7.66
@Contact :   for_freedom_x64@live.com
'''

import sys, os, re
from PyQt6.QtWidgets import QApplication, QPushButton, QFileDialog, QDialog, QTextEdit, QLineEdit, QGridLayout
from PyQt6.QtCore import Qt, pyqtSignal

REDIC = {
    'url' : r'(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?',
    'magnet' : r'(magnet:\?xt=urn:btih:)[0-9a-fA-F]{40}',
    'torrent0' : r'(http|ftp|https):\/\/(.*?\.torrent)',
    'torrent1' : r'file://(/.*?\.torrent)',
    'torrent2' : r'(/Users.*?\.torrent)',
    }

class AddNewDialog(QDialog):

    sinOut = pyqtSignal(tuple)
    #发射元组信号[0]为url地址，其为字典，分为普通地址'urlList'和磁链地址'torrentList'两项内容

    def __init__(self, downloadPath:str=os.path.expanduser('~/Downloads'), urlList:list=None):
        super().__init__()
        self.downloadPath = downloadPath
        self.text = QTextEdit()
        self.text.setPlaceholderText("请输入下载地址,多个地址请用Enter分割")
        if urlList != None:
            urls = ''
            for url in urlList:
                urls += url + '\n'
            self.text.setText(urls)
        self.text.setAcceptRichText(False)
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
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
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
            urls = {'urlList': [], 'torrentList': []}
            #校验是否为url或magnet
            for item in text.split('\n'):
                temp1 = re.findall(REDIC['url'], item)
                temp2 = re.findall(REDIC['magnet'], item)
                if temp1 != [] or temp2 != []:
                    urls['urlList'].append(item)
                    continue
                temp3 = re.findall(REDIC['torrent1'], item)
                temp4 = re.findall(REDIC['torrent2'], item)
                temp0 = re.findall(REDIC['torrent0'], item)
                if temp0 != []:
                    urls['torrentList'].append(item)
                    continue
                elif temp3 != []:
                    urls['torrentList'].append(temp3[0])
                    continue
                elif temp4 != []:
                    urls['torrentList'].append(temp4[0])
                    continue
            dir = self.dirEdit.text()
            self.sinOut.emit((urls,dir))
            print((urls,dir))
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    exe = AddNewDialog(os.path.expanduser('~/Downloads'),['aaa'])
    exe.show()
    sys.exit(app.exec())