#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2022/03/26 16:56:04
@File    :   settingPage.py
@Software:   VSCode
@Author  :   PPPPAN 
@Version :   0.1.75
@Contact :   for_freedom_x64@live.com
'''

import sys, os, time, configparser
import urllib.request
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QScrollArea, QFormLayout, QLineEdit, QTextEdit,QGridLayout, QComboBox, QCompleter, QSpinBox
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QMutex

TESTDIC  = {
    'conf-path' :   '/Users/panzk/.config/aria2/aria2.conf',
    'dir'       :   '/Users/panzk/Downloads',
    'user-agent':   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:98.0) Gecko/20100101 Firefox/98.0',
    'max-concurrent-downloads'      :   '5',
    'max-connection-per-server'     :   '16',
    'max-overall-upload-limit'      :   '1K',
    'max-overall-download-limit'    :   '0',
    'rpc-listen-port'               :   '6800',
    'bt-tracker':   'udp://tracker.coppersurfer.tk:6969/announce,udp://tracker.leechers-paradise.org:6969/announce,udp://tracker.opentrackr.org:1337/announce,udp://p4p.arenabg.com:1337/announce,udp://9.rarbg.to:2710/announce,udp://9.rarbg.me:2710/announce,udp://tracker.internetwarriors.net:1337/announce,udp://exodus.desync.com:6969/announce,udp://tracker.tiny-vps.com:6969/announce,udp://tracker.moeking.me:6969/announce,',
    }
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:98.0) Gecko/20100101 Firefox/98.0',
    'Accept' : 'image/avif,image/webp,*/*;video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5',
    'Accept-Encoding': 'UTF-8',
    'Connection': 'keep-alive',
    }
TRACKERURL = [
    'https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best_ip.txt',
    'https://ngosang.github.io/trackerslist/trackers_best_ip.txt',
    'https://cdn.jsdelivr.net/gh/ngosang/trackerslist@master/trackers_best_ip.txt',
    'https://trackerslist.com/best_aria2.txt',
    'https://cdn.jsdelivr.net/gh/XIU2/TrackersListCollection/best_aria2.txt',
    'https://trackerslist.com/best.txt',
    ]
class Thread(QThread):

    sinOut = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.qmut = QMutex() # 创建线程锁

    def run(self):
        self.qmut.lock()
        self.text = ''
        for url in TRACKERURL:
            request = urllib.request.Request(url=url, headers=HEADERS)
            try:
                response = urllib.request.urlopen(request, timeout=10)
                html = response.read()
                html = html.decode('UTF-8')
            except TimeoutError:
                print('不知道哪错了')
            except urllib.error.URLError as e:
                print('URLError')
                if hasattr(e, 'code'):
                    print(e.code)
                if hasattr(e, 'reason'):
                    print(e.reason)
            except urllib.error.HTTPError as e:
                print('HTTPError')
                if hasattr(e, 'code'):
                    print(e.code)
                if hasattr(e, 'reason'):
                    print(e.reason)
            #如果成功,发送得到的html,并退出循环
            else:
                self.text = html
                break
        self.sinOut.emit(self.text)
        self.qmut.unlock()


class SettingPage(QWidget):

    sinOut = pyqtSignal(dict)
    #生成资源文件目录访问路径
    #说明： pyinstaller工具打包的可执行文件，运行时sys。frozen会被设置成True
    #      因此可以通过sys.frozen的值区分是开发环境还是打包后的生成环境
    #
    #      打包后的生产环境，资源文件都放在sys._MEIPASS目录下
    #      修改main.spec中的datas，
    #      如datas=[('res', 'res')]，意思是当前目录下的res目录加入目标exe中，在运行时放在零时文件的根目录下，名称为res
    BASEPATH = ''
    confPath = os.path.expanduser('~') + '/.config/ashore/aria2.conf'
    exeConfPath = 'config'
    if getattr(sys, 'frozen', False):
        BASEPATH = sys._MEIPASS + '/'
        exeConfPath = os.path.dirname(os.path.dirname(sys.executable)) + '/Resources/config'

    def __init__(self):
        super().__init__()
        self.globalConfig = TESTDIC
        if not os.path.exists(self.exeConfPath):
            os.system('mkdir ' + self.exeConfPath)
        if not os.path.exists(self.exeConfPath + '/ashore.conf'):
            os.system('cp ' + self.BASEPATH + 'config/ashore.conf ' + self.exeConfPath)
        self.initUI()

    def initUI(self):
        
        titleLabel = QLabel('设置')
        formLayout = QFormLayout()
        formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.pathLineEdit = QLineEdit('~/Download')
        #设置目录补全
        completer = QCompleter()
        model = QFileSystemModel()
        model.setRootPath(os.path.expanduser('~/Downloads'))
        completer.setModel(model)
        self.pathLineEdit.setCompleter(completer)
        self.pathLineEdit.setMinimumWidth(400)
        formLayout.addWidget(QLabel('基本设置'))
        pathBtn = QPushButton('选择目录')
        pathBtn.setFixedWidth(100)
        pathLayout = QHBoxLayout()
        pathLayout.addWidget(self.pathLineEdit)
        pathLayout.addWidget(pathBtn)
        formLayout.addRow('默认下载目录:', pathLayout)
        
        self.maxDownloadsSpin = QSpinBox()
        self.maxDownloadsSpin.setRange(1, 20)
        self.maxDownloadsSpin.setMinimumWidth(150)
        formLayout.addRow('同时最大下载数:', self.maxDownloadsSpin)
        self.maConnectionSpin = QSpinBox()
        self.maConnectionSpin.setRange(1, 16)
        self.maConnectionSpin.setMinimumWidth(150)
        formLayout.addRow('同一服务器连接数:', self.maConnectionSpin)
        self.userAgentLineEdit = QLineEdit('')
        self.userAgentLineEdit.setMinimumWidth(500)
        formLayout.addRow('User Agent:', self.userAgentLineEdit)
        uploadLimitLabel = QLabel('上传限速')
        self.uploadLimitSpin = QSpinBox()
        self.uploadLimitSpin.setRange(0, 1024)
        self.uploadLimitSpin.setSpecialValueText('不限速') 
        self.uploadLimitSpin.setMinimumWidth(150)
        self.uploadLimitComboBox = QComboBox()
        self.uploadLimitComboBox.addItems(['B/s', 'KB/s', 'MB/s'])
        downloaLimitLabel = QLabel('下载限速') 
        self.downloadLimitSpin = QSpinBox()
        self.downloadLimitSpin.setRange(0, 1024)
        self.downloadLimitSpin.setSpecialValueText('不限速') 
        self.downloadLimitSpin.setMinimumWidth(150)
        self.downloadLimitComboBox = QComboBox()
        self.downloadLimitComboBox.addItems(['B/s', 'KB/s', 'MB/s'])
        transLayout = QGridLayout()
        transLayout.addWidget(uploadLimitLabel,0,0,1,1)
        transLayout.addWidget(self.uploadLimitSpin,0,1,1,1)
        transLayout.addWidget(self.uploadLimitComboBox,0,2,1,1)
        transLayout.addWidget(downloaLimitLabel,1,0,1,1)
        transLayout.addWidget(self.downloadLimitSpin,1,1,1,1)
        transLayout.addWidget(self.downloadLimitComboBox,1,2,1,1)
        formLayout.addRow('限速下载:', transLayout)
        formLayout.addWidget(QLabel('rpc相关'))
        self.rpcPortLineEdit = QLineEdit()
        self.rpcPortLineEdit.setEnabled(False)
        formLayout.addRow('rpc监听端口:', self.rpcPortLineEdit)
        formLayout.addWidget(QLabel('BT设置'))
        self.btTracker = QTextEdit()
        self.btTracker.setMinimumWidth(500)
        self.trackerBtn = QPushButton('更新Tracker')
        self.trackerBtn.setFixedWidth(100)
        self.trackerInfo = QLabel('1')
        trackerLayout = QGridLayout()
        trackerLayout.addWidget(self.btTracker, 0, 0, 1, 2)
        trackerLayout.addWidget(self.trackerInfo, 1, 0, 1, 1)
        trackerLayout.addWidget(self.trackerBtn, 1, 1, 1, 1)
        formLayout.addRow('btTracker:', trackerLayout)

        settingWidget = QWidget()
        settingWidget.setLayout(formLayout)
        settingWidget.setMinimumWidth(600)
        scrollArea = QScrollArea()
        scrollArea.setWidget(settingWidget)
        self.saveBtn = QPushButton('保存')
        self.saveBtn.setFixedWidth(100)
        self.saveInfoLabel = QLabel()
        saveLayout = QHBoxLayout()
        saveLayout.addWidget(self.saveBtn)
        saveLayout.addWidget(self.saveInfoLabel)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(titleLabel)
        mainLayout.addWidget(scrollArea)
        mainLayout.addLayout(saveLayout)

        self.setLayout(mainLayout)
        self.setMinimumWidth(700)

        pathBtn.clicked.connect(self.slotDir)
        self.trackerBtn.clicked.connect(self.slotTracker)
        self.saveBtn.clicked.connect(self.slotSaveConfig)
    
    def updateSetting(self, options:dict):
        self.globalConfig = options
        self.pathLineEdit.setText(options['dir'])
        self.maxDownloadsSpin.setValue(int(options['max-concurrent-downloads']))
        self.maConnectionSpin.setValue(int(options['max-connection-per-server']))
        self.userAgentLineEdit.setText(options['user-agent'])
        self.setMaxLimit(options['max-overall-upload-limit'], 'upload')
        self.setMaxLimit(options['max-overall-download-limit'], 'download')
        self.rpcPortLineEdit.setText(options['rpc-listen-port'])
        self.btTracker.setText(options['bt-tracker'])
        self.trackerInfo.setText(self.getConfDatetime())
    
    def setMaxLimit(self, value, which:str):
        tempNum = 0
        tempIndex = 0
        if value[-1] == 'M' or value[-1] == 'm':
            tempNum = int(value[:-1])
            tempIndex = 2
        elif  value[-1] == 'K' or value[-1] == 'k':
            tempNum = int(value[:-1])
            tempIndex = 1
        elif  value[-1] == 'B':
            tempNum = int(value[:-1])
            tempIndex = 0
        else:
            tempNum= int(value)
            tempIndex = 0
        if which == 'upload':
            self.uploadLimitSpin.setValue(tempNum)
            self.uploadLimitComboBox.setCurrentIndex(tempIndex)
        elif which == 'download':
            self.downloadLimitSpin.setValue(tempNum)
            self.downloadLimitComboBox.setCurrentIndex(tempIndex)

    def getMaxLimit(self, which:str) -> str:
        tempNum = 0
        tempIndex = 0
        if which == 'upload':
            tempNum = self.uploadLimitSpin.value()
            tempIndex = self.uploadLimitComboBox.currentIndex()
        elif which == 'download':
            tempNum = self.downloadLimitSpin.value()
            tempIndex = self.downloadLimitComboBox.currentIndex()
        if tempIndex == 0:
            return str(tempNum)
        elif tempIndex == 1:
            return str(tempNum) + 'K'
        elif tempIndex == 2:
            return str(tempNum) + 'M'

    def getConfDatetime(self) -> str:
        config = configparser.ConfigParser()
        config.read(self.exeConfPath + '/ashore.conf', encoding='UTF-8')
        datetime = config.get('global','trackers_list_time')
        return datetime

    def setConfDatetime(self, datetime:str):
        config = configparser.ConfigParser()
        config.read(self.exeConfPath + '/ashore.conf', encoding='UTF-8')
        config.set('global', 'trackers_list_time', datetime)
        config.write(open(self.exeConfPath + '/ashore.conf', 'w'))
    
    def getDownloadPath(self) -> str:
        return self.globalConfig['dir']

    def slotDir(self):
        path = QFileDialog.getExistingDirectory(self,'Open dir', self.pathLineEdit.text(), QFileDialog.Option.ShowDirsOnly)
        if path != '':
            self.pathLineEdit.setText(path)

    def slotTracker(self):
        self.saveBtn.setEnabled(False)
        self.trackerBtn.setEnabled(False)
        self.trackerBtn.setText('更新中...')
        self.trackerInfo.setText('等待数据')
        #交给线程处理，以免主界面卡死
        self.trakersThreading = Thread()
        self.trakersThreading.sinOut.connect(self.slotShowTrakers)
        self.trakersThreading.start()

    def slotShowTrakers(self, html:str):
        #更新失败
        if html == '':
            self.trackerInfo.setText('更新失败')
        #更新成功
        else:
            trakers = ''
            for item in html.split('\n\n'):
                if item != '':
                    trakers += item + ','
            datetime = time.strftime("%Y.%m.%d %H:%M",time.localtime())
            self.setConfDatetime(datetime)
            self.trackerInfo.setText(datetime)
            self.btTracker.setText(trakers)
            # print(trakers)
        self.trackerBtn.setText('更新Tracker')
        self.trackerBtn.setEnabled(True)
        self.saveBtn.setEnabled(True)

    def slotSaveConfig(self):
        USERCONFIG = {
            'dir'           : self.pathLineEdit.text(),
            'bt-tracker'    : self.btTracker.toPlainText(),
            'max-concurrent-downloads'  :   str(self.maxDownloadsSpin.value()),
            'max-connection-per-server' :   str(self.maConnectionSpin.value()),
            'user-agent'    : self.userAgentLineEdit.text(),
            'max-overall-upload-limit'  :   self.getMaxLimit('upload'),
            'max-overall-download-limit':   self.getMaxLimit('download'),
            } #用户配置界面有的选项
        ######################!!!!!!!!!!!!!!######################
        # configparser是真的坑，不允许没有section的配置文件,还好配置文件里手动加了[global]以后aria2只是警告没有报错
        # 然后
        # configparser读取了配置文件以后还会抹掉注释，不得不修改注释的开头为/，并且允许无值配置
        ######################!!!!!!!!!!!!!!######################
        configFile = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)#得到aria2配置文件
        configFile.read(self.confPath, encoding='UTF-8')
        aria2pDic = self.globalConfig                   #得到aria2p的全局配置字典
        for key,value in USERCONFIG.items():
            self.setConfig(configFile, aria2pDic, key, value)
        self.sinOut.emit(aria2pDic)                     #把修改好的aria2p的全局配置字典发射信号给主程序,让主程序配置运行中的aria2p
        configFile.write(open(self.confPath, 'w'))         #写入aria2配置文件
        self.globalConfig = aria2pDic                   #将修改后的aria2p的全局配置赋给self.globalConfig
        self.updateSetting(self.globalConfig)           #刷新界面
        self.saveInfoLabel.setText('保存成功')
        # print(configFile.get('global','dir'))
        # print(aria2pDic)
    
    def setConfig(self, configFile, aria2pDic, option:str, value:str):  #设置两种来源的配置
        configFile.set('global', option, value)             #修改aria2配置文件
        aria2pDic[option] = value                           #修改aria2p的全局配置字典


        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    exe = SettingPage()
    exe.updateSetting(TESTDIC)
    exe.show()
    sys.exit(app.exec())