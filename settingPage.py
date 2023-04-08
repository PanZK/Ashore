#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/03/26 16:56:04
@File    :   settingPage.py
@Software:   VSCode
@Author  :   PPPPAN 
@Version :   0.7.66
@Contact :   for_freedom_x64@live.com
'''

import sys, os, time, configparser, platform, urllib.request
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QScrollArea, QFormLayout, QLineEdit, QTextEdit,QGridLayout, QComboBox, QCompleter, QSpinBox, QSpacerItem
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QMutex

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
                response = urllib.request.urlopen(request, timeout=30)
                html = response.read()
                html = html.decode('UTF-8')
            except TimeoutError:
                # print('不知道哪错了')
                self.text = 'Error'
            except urllib.error.URLError as e:
                # print('URLError')
                self.text = 'URLError:\t'
                if hasattr(e, 'code'):
                    # print(e.code)
                    self.text += e.code
                if hasattr(e, 'reason'):
                    # print(e.reason)
                    self.text += str(e.reason)
            except urllib.error.HTTPError as e:
                self.text = 'HTTPError:\t'
                if hasattr(e, 'code'):
                    # print(e.code)
                    self.text += e.code
                if hasattr(e, 'reason'):
                    # print(e.reason)
                    self.text += str(e.reason)
            #如果成功,发送得到的html,并退出循环
            #如果所有都失败html内容为Error:XXXXX
            else:
                self.text = html
                break
        self.sinOut.emit(self.text)
        self.qmut.unlock()


class SettingPage(QWidget):

    aria2ConfSinOut = pyqtSignal(dict)
    ashoreConfigSinOut = pyqtSignal(dict)
    #生成资源文件目录访问路径
    #说明： pyinstaller工具打包的可执行文件，运行时sys。frozen会被设置成True
    #      因此可以通过sys.frozen的值区分是开发环境还是打包后的生成环境
    #
    #      打包后的生产环境，资源文件都放在sys._MEIPASS目录下
    #      修改main.spec中的datas，
    #      如datas=[('res', 'res')]，意思是当前目录下的res目录加入目标exe中，在运行时放在零时文件的根目录下，名称为res
    BASEPATH = ''
    aria2ConfPath = os.path.expanduser('~') + '/.config/ashore/aria2.conf'
    ashoreConfDir = 'config'
    if getattr(sys, 'frozen', False):
        #程序运行可能会被加载一个动态生成的虚拟目录或临时目录，以此来获取程序运行真实目录
        BASEPATH = sys._MEIPASS
        #根据系统平台不同，获取不同的程序存放地址（不一定为真实运行目录）
        if platform.system() == 'Darwin':
            ashoreConfDir = os.path.dirname(os.path.dirname(sys.executable)) + '/Resources/config'
        elif platform.system() == 'Linux':
            ashoreConfDir = os.path.dirname(os.path.dirname(sys.executable)) + '/Ashore/config'
        elif platform.system() == 'Windows':
            ashoreConfDir = os.path.dirname(os.path.dirname(sys.executable))

    Aria2Config = {
        'dir'                           :   None,
        'user-agent'                    :   None,
        'max-concurrent-downloads'      :   None,
        'max-connection-per-server'     :   None,
        'max-overall-upload-limit'      :   None,
        'max-overall-download-limit'    :   None,
        'rpc-listen-port'               :   None,
        'bt-tracker'                    :   None,
    }

    AshoreConfig = {
        'trackers_list_time'    : None,
        'quit_with_aria2'       : None,
        'update_interval'       : None,
        'rpc_port_changeable'   : None,
    }

    def __init__(self):
        super().__init__()
        #定义aria2配置字典
        self.globalAria2Conf = self.Aria2Config
        #ashore.conf配置文件路径
        self.ashoreConfPath = self.ashoreConfDir + '/ashore.conf'
        # 可能因第一次运行或目录损坏导致conf目录不存在，则新建目录
        if not os.path.exists(self.ashoreConfDir):
            os.system('mkdir ' + self.ashoreConfDir)
        # 可能因第一次运行或文件损坏导致ashore.conf不存在，将程序自带的复制过去
        if not os.path.exists(self.ashoreConfPath):
            os.system('cp ' + self.BASEPATH + '/config/ashore.conf ' + self.ashoreConfDir)
        #在生成settinpage时就将AshoreConfig注入进来，关于aria2的配置已在aria2Operate加载，则在点开settpage时显示出即可
        self.AshoreConfig = self.getAshoreConfig()
        self.initUI()

    def initUI(self):
        formLayout = QFormLayout()
        formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        # Aira2设置控件 开始
        self.aria2SettingLabel = QLabel('<h3>Aira2 设置</h3>')
        self.aria2SettingLabel.setFixedHeight(50)
        self.aria2SettingLabel.setMargin(10)
        formLayout.addRow(self.aria2SettingLabel)
        formLayout.addWidget(QLabel('基本设置'))
        #设置目录补全
        completer = QCompleter()
        model = QFileSystemModel()
        model.setRootPath(os.path.expanduser('~/Downloads'))
        completer.setModel(model)
        self.pathLineEdit = QLineEdit('~/Download')
        self.pathLineEdit.setCompleter(completer)
        self.pathLineEdit.setMinimumWidth(450)
        pathBtn = QPushButton('选择目录')
        pathBtn.setFixedWidth(100)
        pathLayout = QHBoxLayout()
        pathLayout.addWidget(self.pathLineEdit)
        pathLayout.addWidget(pathBtn)
        formLayout.addRow('默认下载目录:', pathLayout)
        self.maxDownloadsSpin = QSpinBox()
        self.maxDownloadsSpin.setRange(1, 100)
        self.maxDownloadsSpin.setMaximumWidth(100)
        formLayout.addRow('同时最大下载数:', self.maxDownloadsSpin)
        self.maConnectionSpin = QSpinBox()
        self.maConnectionSpin.setRange(1, 16)
        self.maConnectionSpin.setMaximumWidth(100)
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
        self.uploadLimitComboBox.addItems(['B/s', 'KB/s', 'MB/s', 'GB/s'])
        downloaLimitLabel = QLabel('下载限速') 
        self.downloadLimitSpin = QSpinBox()
        self.downloadLimitSpin.setRange(0, 1024)
        self.downloadLimitSpin.setSpecialValueText('不限速') 
        self.downloadLimitSpin.setMinimumWidth(150)
        self.downloadLimitComboBox = QComboBox()
        self.downloadLimitComboBox.addItems(['B/s', 'KB/s', 'MB/s', 'GB/s'])
        transLayout = QGridLayout()
        transLayout.addWidget(uploadLimitLabel,0,0,1,1)
        transLayout.addWidget(self.uploadLimitSpin,0,1,1,1)
        transLayout.addWidget(self.uploadLimitComboBox,0,2,1,1)
        transLayout.addWidget(downloaLimitLabel,1,0,1,1)
        transLayout.addWidget(self.downloadLimitSpin,1,1,1,1)
        transLayout.addWidget(self.downloadLimitComboBox,1,2,1,1)
        transLayout.addItem(QSpacerItem(300,20),0,3,2,1)
        formLayout.addRow('限速设置:', transLayout)
        self.rpcPortLineEdit = QLineEdit()
        self.rpcPortLineEdit.setMaximumWidth(200)
        self.rpcPortLineEdit.setToolTip('Ashore默认端口为6801')
        self.rpcPortLineEdit.setPlaceholderText('Ashore默认端口为6801')
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

        # Ashore设置控件 开始
        self.ashoreSettingLabel = QLabel('<h3>Ashore 设置</h3>')
        self.ashoreSettingLabel.setFixedHeight(50)
        self.ashoreSettingLabel.setMargin(10)
        formLayout.addRow(self.ashoreSettingLabel)
        self.withAria2QuitComboBox = QComboBox()
        self.withAria2QuitComboBox.addItems(['是', '否'])
        quitWithAria2Layout = QHBoxLayout()
        quitWithAria2Layout.addWidget(self.withAria2QuitComboBox)
        quitWithAria2Layout.addStretch(10)
        formLayout.addRow('aria2随程序关闭:', quitWithAria2Layout)
        self.updateIntervalSpin = QSpinBox()
        self.updateIntervalSpin.setRange(500, 10000)
        self.updateIntervalSpin.setSingleStep(100)
        self.updateIntervalSpin.setMaximumWidth(100)
        updateIntervalLabel = QLabel('毫秒')
        updateIntervalLayout = QHBoxLayout()
        updateIntervalLayout.addWidget(self.updateIntervalSpin)
        updateIntervalLayout.addWidget(updateIntervalLabel)
        formLayout.addRow('界面刷新间隔:', updateIntervalLayout)
        self.rpcPortChangeableComboBox = QComboBox()
        self.rpcPortChangeableComboBox.addItems(['是', '否'])
        rpcPortChangeableLayout = QHBoxLayout()
        rpcPortChangeableLayout.addWidget(self.rpcPortChangeableComboBox)
        rpcPortChangeableLayout.addStretch(10)
        formLayout.addRow('允许修改rpc接口:', rpcPortChangeableLayout)

        settingWidget = QWidget()
        settingWidget.setLayout(formLayout)
        settingWidget.setContentsMargins(20,0,0,0)
        # settingWidget.setMinimumWidth(400)
        scrollToAria2Btn = QPushButton('Aria2 设置')
        scrollToAria2Btn.setFixedWidth(120)
        scrollToAshoreBtn = QPushButton('Ashore 设置')
        scrollToAshoreBtn.setFixedWidth(120)
        self.saveBtn = QPushButton('保存设置')
        self.saveBtn.setFixedWidth(120)
        scrollBtnLayout = QVBoxLayout()
        scrollBtnLayout.addWidget(scrollToAria2Btn)
        scrollBtnLayout.addWidget(scrollToAshoreBtn)
        scrollBtnLayout.addStretch(10)
        scrollBtnLayout.addWidget(self.saveBtn)
        scrollBtnLayout.setContentsMargins(10,0,10,0)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(settingWidget)

        mainLayout = QHBoxLayout()
        mainLayout.addLayout(scrollBtnLayout)
        mainLayout.addWidget(self.scrollArea)

        self.setLayout(mainLayout)
        self.setMinimumWidth(945)

        # 生成时先更新已获取的Ashore配置部分
        # self.updateAhoreSetting(self.AshoreConfig)

        pathBtn.clicked.connect(self.slotDir)
        scrollToAria2Btn.clicked.connect(self.slotScrollToAria2)
        scrollToAshoreBtn.clicked.connect(self.slotScrollToAshore)
        self.trackerBtn.clicked.connect(self.slotTracker)
        self.saveBtn.clicked.connect(self.slotSaveConf)
        self.rpcPortChangeableComboBox.currentIndexChanged.connect(self.slotRpcPortChangeable)
    
    def updateSettingPage(self, aria2Config:dict):
        self.updateAria2Setting(aria2Config)
        self.updateAhoreSetting(self.AshoreConfig)

    def updateAria2Setting(self, aria2Config:dict):
        self.globalAria2Conf = aria2Config
        self.pathLineEdit.setText(aria2Config['dir'])
        self.maxDownloadsSpin.setValue(int(aria2Config['max-concurrent-downloads']))
        self.maConnectionSpin.setValue(int(aria2Config['max-connection-per-server']))
        self.userAgentLineEdit.setText(aria2Config['user-agent'])
        self.setMaxLimit(aria2Config['max-overall-upload-limit'], 'upload')
        self.setMaxLimit(aria2Config['max-overall-download-limit'], 'download')
        self.rpcPortLineEdit.setText(aria2Config['rpc-listen-port'])
        self.btTracker.setText(aria2Config['bt-tracker'])

    def updateAhoreSetting(self, ashoreConfig:dict):
        self.trackerInfo.setText(ashoreConfig['trackers_list_time'])
        self.setBoolOption(self.withAria2QuitComboBox, ashoreConfig['quit_with_aria2'])
        self.setBoolOption(self.rpcPortChangeableComboBox, ashoreConfig['rpc_port_changeable'])
        self.updateIntervalSpin.setValue(int(ashoreConfig['update_interval']))
        self.rpcPortLineEdit.setEnabled(ashoreConfig['rpc_port_changeable'])

    def setMaxLimit(self, value, which:str):
        #将running中的aria2限速配置显示在settingpage上
        tempNum = 0
        tempIndex = 0
        #若限速以单位结尾
        if value[-1] == 'G' or value[-1] == 'g':
            tempNum = int(value[:-1])
            tempIndex = 3
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
            #若限速无单位结尾为纯byte的数字
            value = int(value)
            if value < 1024:
                tempNum = value
                tempIndex = 0
            elif value < 1048576:
                tempNum = int(value/1024)
                tempIndex = 1
            elif value < 1073741824:
                tempNum = int(value/1048576)
                tempIndex = 2
            else:
                tempNum = int(value/1073741824)
                tempIndex = 3
        if which == 'upload':
            self.uploadLimitSpin.setValue(tempNum)
            self.uploadLimitComboBox.setCurrentIndex(tempIndex)
        elif which == 'download':
            self.downloadLimitSpin.setValue(tempNum)
            self.downloadLimitComboBox.setCurrentIndex(tempIndex)

    def getMaxLimit(self, which:str) -> str:
        #将settingpage上带单位的限速设置写入aria2.conf
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
        elif tempIndex == 3:
            return str(tempNum) + 'G'

    def getBoolOption(self, boolObject:QComboBox) -> str:
        index = boolObject.currentIndex()
        if index == 0:
            return 'true'
        elif index == 1:
            return 'false'

    def setBoolOption(self, boolObject:QComboBox, flag:bool) -> None:
        if flag == True:
            boolObject.setCurrentIndex(0)
        elif flag == False:
            boolObject.setCurrentIndex(1)

    def getAshoreConfig(self) -> dict:
        ashoreConfig = configparser.ConfigParser()
        ashoreConfig.read(self.ashoreConfPath, encoding='UTF-8')
        tempDict = {}
        for key in self.AshoreConfig.keys():
            value = ashoreConfig.get('global', key)
            if value == 'true':
                value = True
            elif value == 'false':
                value = False
            tempDict[key] = value
        return tempDict

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
        beginner = html[:6]
        #更新失败
        if beginner != 'http:/' and beginner != 'udp://' and beginner != 'https:':
            self.trackerInfo.setText('更新失败')
        #更新成功
        else:
            trakers = ''
            for item in html.split('\n\n'):
                if item != '':
                    trakers += item + ','
            datetime = time.strftime("%Y.%m.%d %H:%M",time.localtime())
            self.trackerInfo.setText(datetime)
            self.btTracker.setText(trakers)
        self.trackerBtn.setText('更新Tracker')
        self.trackerBtn.setEnabled(True)
        self.saveBtn.setEnabled(True)

    def slotSaveConf(self) -> None:
        #用户配置界面有的选项
        UserAria2Conf = {
            'dir'                       :   self.pathLineEdit.text(),
            'bt-tracker'                :   self.btTracker.toPlainText(),
            'max-concurrent-downloads'  :   str(self.maxDownloadsSpin.value()),
            'max-connection-per-server' :   str(self.maConnectionSpin.value()),
            'user-agent'                :   self.userAgentLineEdit.text(),
            'max-overall-upload-limit'  :   self.getMaxLimit('upload'),
            'max-overall-download-limit':   self.getMaxLimit('download'),
            'rpc-listen-port'           :   self.rpcPortLineEdit.text()
            }
        UserAshoreConf ={
            'trackers_list_time'    :   self.trackerInfo.text(),
            'quit_with_aria2'       :   self.getBoolOption(self.withAria2QuitComboBox),
            'update_interval'       :   str(self.updateIntervalSpin.value()),
            'rpc_port_changeable'   :   self.getBoolOption(self.rpcPortChangeableComboBox),
        }
        if self.saveAria2Conf(UserAria2Conf) == 0:
            self.aria2ConfSinOut.emit(self.globalAria2Conf)                 #把修改好的aria2的全局配置字典发射信号给主程序,让主程序配置运行中的aria2
        else:
            self.aria2ConfSinOut.emit(self.UserAria2Conf)                   #若报错则发射用户界面配置信息
        if self.saveAshoreConf(UserAshoreConf) == 0:
            UserAshoreConf.update({'isSaved' : '保存成功'})                    #成功则增加一条信息‘保存成功’
            self.ashoreConfigSinOut.emit(UserAshoreConf)                        #发射信号
        else:
            UserAshoreConf.update({'isSaved' : '保存失败'})                    #成功则增加一条信息‘保存失败’
            self.ashoreConfigSinOut.emit(UserAshoreConf)                        #发射信号

        ######################!!!!!!!!!!!!!!######################
        # configparser不允许没有section的配置文件,还好配置文件里手动加了[global]以后aria2只是警告没有报错
        # 然后
        # configparser读取了配置文件以后还会抹掉注释，不得不修改注释的开头为/，并且允许无值配置
        ######################!!!!!!!!!!!!!!######################
    def saveAria2Conf(self, UserAria2Conf:dict) -> int:
        configFile = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)#得到aria2配置文件
        configFile.read(self.aria2ConfPath, encoding='UTF-8')
        #更新程序内存中configFile与运行中aria2的配置，准备发送
        for key,value in UserAria2Conf.items():
            self.globalAria2Conf[key] = value                           #修改aria2的全局配置字典
            configFile.set('global', key, value)                        #修改aria2配置文件
        with open(self.aria2ConfPath, 'w', encoding='utf-8') as file:   #写入aria2配置文件
            configFile.write(file)
        return 0

    def saveAshoreConf(self, UserAshoreConf:dict) -> int:
        configFile = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)#得到Ashore配置文件
        configFile.read(self.ashoreConfPath, encoding='UTF-8')
        #更新程序内存中configFile与运行中Ashore的配置，准备发送
        for key,value in UserAshoreConf.items():
            configFile.set('global', key, value)                        #修改Ashore配置文件
        with open(self.ashoreConfPath, 'w', encoding='utf-8') as file:  #写入Ashore配置文件
            configFile.write(file)
        return 0

    def slotRpcPortChangeable(self, index:int=1) -> None:
        #将rpc port LineEdit设置为相应状态
        self.rpcPortLineEdit.setEnabled(not index)

    def slotScrollToAria2(self) -> None:
        self.scrollArea.verticalScrollBar().setValue(self.aria2SettingLabel.y())

    def slotScrollToAshore(self) -> None:
        self.scrollArea.verticalScrollBar().setValue(self.ashoreSettingLabel.y())


if __name__ == '__main__':
    TESTDIC  = {
    # 'conf-path' :   '/Users/panzk/.config/ashore/aria2.conf',
    'dir'       :   os.path.expanduser('~')+'/下载',
    'user-agent':   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:98.0) Gecko/20100101 Firefox/98.0',
    'max-concurrent-downloads'      :   '20',
    'max-connection-per-server'     :   '16',
    'max-overall-upload-limit'      :   '11K',
    'max-overall-download-limit'    :   '0',
    'rpc-listen-port'               :   '6801',
    'bt-tracker':   'udp://tracker.coppersurfer.tk:6969/announce,udp://tracker.leechers-paradise.org:6969/announce,udp://tracker.opentrackr.org:1337/announce,udp://p4p.arenabg.com:1337/announce,udp://9.rarbg.to:2710/announce,udp://9.rarbg.me:2710/announce,udp://tracker.internetwarriors.net:1337/announce,udp://exodus.desync.com:6969/announce,udp://tracker.tiny-vps.com:6969/announce,udp://tracker.moeking.me:6969/announce,',
    }
    app = QApplication(sys.argv)
    exe = SettingPage()
    exe.updateSettingPage(TESTDIC)
    exe.show()
    sys.exit(app.exec())