#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/03/20 20:12:13
@File    :   Ashore.py
@Software:   VSCode
@Author  :   PPPPAN 
@Version :   0.7.66
@Contact :   for_freedom_x64@live.com
'''

import sys, os, platform
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedLayout, QSplashScreen, QMenu, QLabel, QStatusBar, QSystemTrayIcon
from PyQt6.QtGui import QIcon, QPixmap, QAction, QDesktopServices, QFont
from PyQt6.QtCore import QTimer, QSize, QEvent, QUrl, pyqtSignal, QObject, QThread, Qt
from page import Page
from aria2Operate import Aria2Operate
from addNewDialog import AddNewDialog
from settingPage import SettingPage

DEFAULTPATH = os.path.expanduser('~/Downloads')
class Aria2Thread(Aria2Operate, QThread):

    updatedSignal = pyqtSignal(dict)

    def __init__(self, BASEPATH:str=None, QuitWithAria2:bool=False, UpdateInterval:int=2000):
        #传递参数运行基本目录
        super().__init__(BASEPATH=BASEPATH, QuitWithAria2=QuitWithAria2)
        QObject.__init__(self)
        self.timer = QTimer()  # 初始化一个定时器
        self.timer.timeout.connect(self.start)  # 每次计时到时间时发出信号
        self.timer.start(UpdateInterval)  # 设置计时间隔并启动；单位毫秒

    def run(self):
        # self.timer.stop()
        self.myPrint('----------------new request-----------------')
        self.updatedSignal.emit(self.getMissions())
        # missions = self.getMissions()
        # if 'ResultError' in missions:
        # # # self.timer.start()
        #     self.updatedSignal.emit((0, missions))
        # else:
        #     self.updatedSignal.emit((missions, 0)

    def performan(self, host="http://localhost", port=6801, secret="", data:str='{}', numRetry:int=7) -> dict:
        result = Aria2Operate.performan(self, host=host, port=port, secret=secret, data=data, numRetry=numRetry)
        return result

class Ashore(QMainWindow):
    def __init__(self):
        super().__init__()
        # Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint
        #生成资源文件目录访问路径
        #上限2000个任务
        #说明： pyinstaller工具打包的可执行文件，运行时sys。frozen会被设置成True
        #      因此可以通过sys.frozen的值区分是开发环境还是打包后的生成环境
        #
        #      打包后的生产环境，资源文件都放在sys._MEIPASS目录下
        #      修改main.spec中的datas，
        #      如datas=[('res', 'res')]，意思是当前目录下的res目录加入目标exe中，在运行时放在零时文件的根目录下，名称为res
        self.isRelease = False
        self.BASEPATH = ''
        # getattr 函数判断第一参数中是否含有第二参数这个属性：有则返回True，若没有：当第三参数为空时返回error，第三参数存在则返回第三参数
        if getattr(sys, 'frozen', False):
            self.isRelease = True
            #判断是否为发布状态，利用系统方法找到运行目录
            self.BASEPATH = sys._MEIPASS + '/'        
        self.pageSetting = SettingPage()
        #获取ashore配置信息
        ashoreConfig = self.pageSetting.getAshoreConfig()
        self.aria2Operate = Aria2Thread(
            BASEPATH=self.BASEPATH,
            QuitWithAria2=ashoreConfig['quit_with_aria2'],
            UpdateInterval=int(ashoreConfig['update_interval'])
            )

        self.initUI()
        self.setConnect()
        self.updatePage()
        self.aria2Operate.updatedSignal.connect(self.updatePage)

    def createMenuBar(self) -> None:
        menuBar = self.menuBar()
        newAction = QAction('新建下载',self, triggered=self.slotClickBtnAddNew)
        newAction.setStatusTip('新建下载任务')
        newAction.setShortcut('Ctrl+N')
        saveAction = QAction('保存会话',self, triggered=self.slotSaveSession)
        saveAction.setStatusTip('保存下载任务')
        saveAction.setShortcut('Ctrl+S')
        restartAction = QAction('重启Aria2',self, triggered=self.slotRestartAria2)
        restartAction.setStatusTip('重新启动Aria2,可能导致程序短暂卡顿')
        quitAction = QAction('退出程序',self, triggered=self.slotQuit)
        quitAction.setStatusTip('彻底退出程序')
        quitAction.setShortcut('Ctrl+Q')
        fileMenu = menuBar.addMenu("文件")
        fileMenu.addAction(newAction)
        fileMenu.addAction(saveAction)
        fileMenu.addSeparator()
        fileMenu.addAction(restartAction)
        fileMenu.addAction(quitAction)
        unpauseAllAction = QAction('开始全部',self, triggered=self.slotUnpauseAll)
        unpauseAllAction.setStatusTip('开始全部任务')
        pauseAllAction = QAction('暂停全部',self, triggered=self.slotPauseAll)
        pauseAllAction.setStatusTip('逐步暂停全部任务')
        editMenu = menuBar.addMenu("编辑")
        editMenu.addAction(unpauseAllAction)
        editMenu.addAction(pauseAllAction)
        showAction = QAction('显示窗口',self, triggered=self.show)
        showAction.setShortcut('Ctrl+R')
        hideAction = QAction('关闭窗口',self, triggered=self.hide)
        hideAction.setStatusTip('退出当前应用')
        hideAction.setShortcut('Ctrl+W')
        windowMenu = menuBar.addMenu("窗口")
        windowMenu.addAction(showAction)
        windowMenu.addAction(hideAction)
        aboutInfoAction = QAction("关于Ashore", self, triggered=self.slotAbout)
        aboutInfoAction.setStatusTip('关于Ashore')
        helpMenu = menuBar.addMenu("帮助")
        helpMenu.addAction(aboutInfoAction)
        self.setMenuBar(menuBar)

    def createTrayIcon(self) -> None:   #设置菜单栏程序图标及功能
        showWindowAction = QAction("显示主窗口", self, triggered=self.slotShowWindow)
        newAction = QAction('新建下载',self, triggered=self.slotClickBtnAddNew)
        aboutInfoAction = QAction("关于Ashore", self, triggered=self.slotAbout)
        quitAction = QAction("退出", self, triggered=self.slotQuit)
        trayMenu = QMenu()
        trayMenu.addAction(showWindowAction)
        trayMenu.addAction(newAction)
        trayMenu.addSeparator()
        trayMenu.addAction(aboutInfoAction)
        trayMenu.addAction(quitAction)
        self.TrayIcon = QSystemTrayIcon(self)
        self.TrayIcon.setContextMenu(trayMenu)
        self.TrayIcon.setToolTip('Ashore')
        self.TrayIcon.setIcon(QIcon(self.BASEPATH + "static/icon/icon.funtion/trayIcon.png"))
        self.TrayIcon.show()


    def createStatusBar(self) -> None:   #设置状态栏
        self.downSpeedIcon = QLabel('upSpeedIcon')
        self.downSpeedIcon.setFixedSize(20,20)
        self.downSpeedIcon.setScaledContents(True)
        self.downSpeedIcon.setPixmap(QPixmap(self.BASEPATH + 'static/icon/icon.funtion/downloadSpeed.png'))
        self.downSpeedIcon.setToolTip('下载速度')
        self.downSpeedIcon.setStatusTip('全局实时下载速度')
        self.downSpeedLabel = QLabel('下载速度')
        self.downSpeedLabel.setMinimumWidth(80)
        self.downSpeedLabel.setToolTip('下载速度')
        self.downSpeedLabel.setStatusTip('全局实时下载速度')
        self.upSpeedIcon = QLabel('upSpeedIcon')
        self.upSpeedIcon.setFixedSize(20,20)
        self.upSpeedIcon.setScaledContents(True)
        self.upSpeedIcon.setPixmap(QPixmap(self.BASEPATH + 'static/icon/icon.funtion/uploadSpeed.png'))
        self.upSpeedIcon.setToolTip('上传速度')
        self.upSpeedIcon.setStatusTip('全局BT、磁链上传速度')
        self.upSpeedLabel = QLabel('上传速度')
        self.upSpeedLabel.setMinimumWidth(80)
        self.upSpeedLabel.setToolTip('上传速度')
        self.upSpeedLabel.setStatusTip('全局BT、磁链上传速度')
        self.statusBar = QStatusBar()
        self.statusBar.setContentsMargins(0,1,10,2)
        self.statusBar.addPermanentWidget(self.downSpeedIcon)
        self.statusBar.addPermanentWidget(self.downSpeedLabel)
        self.statusBar.addPermanentWidget(self.upSpeedIcon)
        self.statusBar.addPermanentWidget(self.upSpeedLabel)
        self.setStatusBar(self.statusBar)

    def initUI(self) -> None:
        self.tabDownloading = QPushButton(QIcon(self.BASEPATH + 'static/icon/icon.funtion/download.png'),'')
        self.tabDownloading.setFlat(True)
        self.tabDownloading.setIconSize(QSize(23,23))
        self.tabDownloading.setToolTip('下载中')
        self.tabDownloading.setStatusTip('显示所有下载、等待、暂停中的任务')
        self.tabDownloading.setEnabled(False)
        self.tabDownloaded = QPushButton(QIcon(self.BASEPATH + 'static/icon/icon.funtion/completed.png'),'')
        self.tabDownloaded.setFlat(True)
        self.tabDownloaded.setIconSize(QSize(23,23))
        self.tabDownloaded.setToolTip('已完成')
        self.tabDownloaded.setStatusTip('显示所有已完成、错误的任务')
        self.tabSetting = QPushButton(QIcon(self.BASEPATH + 'static/icon/icon.funtion/setting.png'),'')
        self.tabSetting.setFlat(True)
        self.tabSetting.setIconSize(QSize(23,23))
        self.tabSetting.setToolTip('设置')
        self.tabSetting.setStatusTip('Ashore及aria2相关设置')
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
        self.addBtn.setStatusTip('新建下载任务')
        self.addBtn.setShortcut("Ctrl+N")
        self.unpauseAllBtn = QPushButton(QIcon(self.BASEPATH + 'static/icon/icon.funtion/play.png'),'')
        self.unpauseAllBtn.setFlat(True)
        self.unpauseAllBtn.setIconSize(QSize(20,20))
        self.unpauseAllBtn.setToolTip('开始全部')
        self.unpauseAllBtn.setStatusTip('恢复所有暂停的任务')
        self.pauseAllBtn = QPushButton(QIcon(self.BASEPATH + 'static/icon/icon.funtion/pause.png'),'')
        self.pauseAllBtn.setFlat(True)
        self.pauseAllBtn.setIconSize(QSize(20,20))
        self.pauseAllBtn.setToolTip('暂停全部')
        self.pauseAllBtn.setStatusTip('暂停所有下载中的任务')
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.addBtn)
        btnLayout.addWidget(self.unpauseAllBtn)
        btnLayout.addWidget(self.pauseAllBtn)
        #添加弹簧
        btnLayout.addStretch(10)
        self.pageDownloading = Page()
        self.pageDownloaded = Page()
        #pageSetting在程序初始运行时为加载配置已生成
        # self.pageSetting = SettingPage()
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
        self.setMinimumSize(1000,520)
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
        self.createStatusBar()
        self.createTrayIcon()

    def setConnect(self) -> None:
        self.addBtn.clicked.connect(self.slotClickBtnAddNew)
        self.unpauseAllBtn.clicked.connect(self.slotUnpauseAll)
        self.pauseAllBtn.clicked.connect(self.slotPauseAll)
        self.tabDownloading.clicked.connect(self.slotSwitchDownloading)
        self.tabDownloaded.clicked.connect(self.slotSwitchDownloaded)
        self.tabSetting.clicked.connect(self.slotSwitchSetting)
        self.pageSetting.aria2ConfSinOut.connect(self.slotUpdateRunningAria2Config)
        self.pageSetting.ashoreConfigSinOut.connect(self.slotUpdateRunningAshoreConfig)

    def updatePage(self, missions:dict=None) -> None:
        #先获取全局状态信息
        globalStatus = self.aria2Operate.getGlobalStatus()
        if 'ResultError' in globalStatus:
             #包含错误信息，认为任务信息有误，直接报错
            self.myPrint(globalStatus['ResultError'])
            return
        else:
            #没报错处理任务字典
            if missions == None:
                #若为空调用，则主动获取
                missions = self.aria2Operate.getMissions()
            else:
                #若为参数调用，判断参数内容
                if 'ResultError' in missions:
                    #包含错误信息，认为任务信息有误，直接报错
                    self.myPrint(missions['ResultError'])
                    return
            self.pageDownloading.updateSections({'active' : missions['active'], 'waiting' : missions['waiting'], 'paused' : missions['paused']})
            self.pageDownloaded.updateSections({'completed' : missions['completed'] , 'error' : missions['error']})
            self.downSpeedLabel.setText(self.getSpeedStr(int(globalStatus['downloadSpeed'])))
            self.upSpeedLabel.setText(self.getSpeedStr(int(globalStatus['uploadSpeed'])))
        self.setConnectByDic()

    def setConnectByDic(self) -> None:
        for item in self.pageDownloading.sectionsDic.values():
            item.disconnect()
            # 双击section和点击section中开始/暂停按钮效果同步
            item.doubleClickOut.connect(self.slotDoubleClick)
            item.openDirOut.connect(self.slotOpenFolder)
            item.cpUrlOut.connect(self.slotcpUrl)
            item.removeDelOut.connect(self.slotRemoveDel)
        for item in self.pageDownloaded.sectionsDic.values():
            item.disconnect()
            # 双击section和点击section中开始/暂停按钮效果同步
            item.doubleClickOut.connect(self.slotDoubleClick)
            item.openDirOut.connect(self.slotOpenFolder)
            item.cpUrlOut.connect(self.slotcpUrl)
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

    def slotSwitchDownloading(self) -> None:
        self.tabDownloading.setEnabled(False)
        self.tabDownloaded.setEnabled(True)
        self.tabSetting.setEnabled(True)
        self.pageStack.setCurrentIndex(0)

    def slotSwitchDownloaded(self) -> None:
        self.tabDownloading.setEnabled(True)
        self.tabDownloaded.setEnabled(False)
        self.tabSetting.setEnabled(True)
        self.pageStack.setCurrentIndex(1)

    def slotSwitchSetting(self) -> None:
        config = self.aria2Operate.getGlobalConfig()
        if 'ResultError' in config:
            self.myPrint(config['ResultError'])
            return
        else:
            self.tabDownloading.setEnabled(True)
            self.tabDownloaded.setEnabled(True)
            self.tabSetting.setEnabled(False)
            self.pageSetting.updateSettingPage(config)
            self.pageStack.setCurrentIndex(2)

    def addNew(self, urlList:list=[]) -> None:
        """通过命令行参数或系统接口参数运行程序、添加新任务
        :param urlList: list类型的下载地址url
        """
        config = {'ResultError' : 0}
        while 'ResultError' in config:
            config = self.aria2Operate.getGlobalConfig()
        if 'ResultError' in config:
            self.myPrint(config['ResultError'])
            return
        else:
            form = AddNewDialog(config['dir'], urlList)
            form.sinOut.connect(self.aria2Operate.addUrls)
            form.show()
            form.exec()
            self.updatePage()

    def slotClickBtnAddNew(self) -> None:
        """用户通过按钮触发的添加新任务,无参数
        """
        self.addNew()

    def slotUnpauseAll(self):
        unpauseAllResult = self.aria2Operate.unpauseAll()
        if 'ResultError' in unpauseAllResult:
            self.myPrint(unpauseAllResult['ResultError'])

    def slotPauseAll(self):
        pauseAllResult = self.aria2Operate.pauseAll()
        if 'ResultError' in pauseAllResult:
            self.myPrint(pauseAllResult['ResultError'])

    def slotAbout(self):
        aboutTitle = QLabel('<h1 style="Text-align: center;">Ashore</h1>')
        aboutTitle.setFixedHeight(30)
        infoLIcon = QLabel()
        infoLIcon.setPixmap(QPixmap(self.BASEPATH + 'static/icon/icon.funtion/icon0.png'))
        infoLIcon.setScaledContents(True)
        infoLIcon.setFixedSize(180, 180)
        aria2Version = self.aria2Operate.getAria2Version()
        aboutText = QLabel('由Python编写的aira2可视化程序<br>作者:PPPPAN<br>项目地址:<a href="https://github.com/PanZK/Ashore">Github/Ashore</a><br>Python version:3.10.6<br>Ashore version: 1.76.2<br>aria2 version:' + aria2Version)
        aboutText.setOpenExternalLinks(True)
        aboutText.setFixedWidth(300)
        aboutText.setMargin(30)
        aboutLayout = QHBoxLayout()
        aboutLayout.addWidget(infoLIcon)
        aboutLayout.addWidget(aboutText)
        aboutLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        aboutInfoLayout = QVBoxLayout()
        aboutInfoLayout.addWidget(aboutTitle)
        aboutInfoLayout.addLayout(aboutLayout)
        aboutInfoLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.aboutInfo = QWidget()
        self.aboutInfo.setFixedSize(600, 320)
        self.aboutInfo.setLayout(aboutInfoLayout)
        self.aboutInfo.show()

    def slotShowWindow(self):
        self.show()

    def slotSaveSession(self):
        saveResult = self.aria2Operate.saveSession()
        if 'ResultError' in saveResult:
            self.myPrint(saveResult['ResultError'])

    def slotQuit(self):
        self.aria2Operate.saveSession()
        # print("调用sys.exit() 销毁对象，释放其空间")
        if self.aria2Operate.mainKillAria2():
            sys.exit(0)

    def slotRestartAria2(self):
        self.aria2Operate.restartAria2(self.BASEPATH)

    def slotDoubleClick(self, data:tuple) -> None:
        gid = data[0]
        status = data[1]
        #根据section状态判定双击的作用是开始或暂停
        if status == 'active' or status == 'waiting' :
            self.aria2Operate.pause(gid)
        elif status == 'paused':
            self.aria2Operate.unpause(gid)
        elif status == 'completed':
            filePathResult = self.aria2Operate.getFilePath(gid)
            if 'ResultError' in filePathResult:
                self.myPrint(filePathResult['ResultError'])
            else:
                QDesktopServices.openUrl(QUrl.fromLocalFile(filePathResult['filePath']))
        elif status == 'error':
            self.aria2Operate.retry(gid)
        self.updatePage()

    def slotOpenFolder(self, gid:str) -> None:
        OpenResult = self.aria2Operate.openFileDir(gid)
        if 'ResultError' in OpenResult:
            self.myPrint(OpenResult['ResultError'])
        elif 'dir' in OpenResult:
            #返回非空,含有目录地址，代表使用不同系统特色方法调用失败,使用通用办法
            QDesktopServices.openUrl(QUrl.fromLocalFile(OpenResult['dir']))

    def slotcpUrl(self, gid:str) -> None:
        urlResult = self.aria2Operate.getUrl(gid)
        if 'ResultError' in urlResult:
            self.myPrint(urlResult['ResultError'])
        else:
            clipboard = QApplication.clipboard()
            clipboard.setText(urlResult['url'])
            self.myPrint('已复制到剪贴板')        

    def slotRemoveDel(self, data:tuple) -> None:
        gid = data[0]
        delFile = data[1]
        result = self.aria2Operate.delRemoveMission(gid=gid, delFile=delFile)
        if 'ResultError' in result:
            self.myPrint(result['ResultError'])
        else:
            self.myPrint('删除成功')
        self.updatePage()

    def slotUpdateRunningAria2Config(self, conf:dict) -> None:
        # 将setting页面的设置信息更新到运行的aria2程序中
        result = self.aria2Operate.setGlobalConfig(conf)
        if 'ResultError' in result:
            self.myPrint(result['ResultError'])

    def slotUpdateRunningAshoreConfig(self, conf:dict) -> None:
        # 将setting页面的设置信息更新到运行的ashore程序中
        if conf['quit_with_aria2'] == 'false':
            self.aria2Operate.QuitWithAria2 = False
        elif conf['quit_with_aria2'] == 'true':
            self.aria2Operate.QuitWithAria2 = True
        self.aria2Operate.timer.setInterval(int(conf['update_interval']))
        self.myPrint(conf['isSaved'])

    def myPrint(self, data, end=None):
        if type(data) == int:
            #是int的错误代码
            # self.aria2Operate.ERRORLIST[data]
            self.statusBar.showMessage(self.aria2Operate.ERRORLIST[data], 3000)
        else:
            #将提示信息显示在状态栏中showMessage（‘提示信息’，显示时间（单位毫秒））
            self.statusBar.showMessage(data, 3000)
            if not self.isRelease:
                #当程序处于coding阶段时允许输出，当为release时禁止输出
                print(data, end=end)

    def slotShowMessage(self, data:dict):
        """保留函数
            由于目前没有找到接收json-rpc信息的方法,故先保留信息推送功能
        """
        self.TrayIcon.showMessage('1111111','111111')

class MyApplication(QApplication):

    fileOpenSignal = pyqtSignal(list)

    def __init__(self, arguments):
        super().__init__(arguments)
        self.setQuitOnLastWindowClosed(False)    #设置关闭窗口后最小化
        self.setApplicationVersion('0.2.05')
        self.setOrganizationName('PanZK')
        self.setApplicationName("Ashore")

    def event(self, event):
        if event.type() == QEvent.Type.FileOpen:    # 对请求进行判断
            self.fileOpenSignal.emit([event.url().toString()])
        return super().event(event)

if __name__ == '__main__':
    BASEPATH = ''
    if getattr(sys, 'frozen', False):
        BASEPATH = sys._MEIPASS + '/'
    app = MyApplication(sys.argv)
    splash = QSplashScreen(QPixmap(BASEPATH + 'static/img/cover.png'))
    splash.show()                               #展示启动图片
    app.processEvents()                         #防止进程卡死
    if platform.system() == 'Darwin':
        app.setFont(QFont('Hiragino Sans GB'))  #防止mac系统上运行速度受阻，选用“冬青黑体简体中文”为默认字体
        app.setWindowIcon(QIcon(BASEPATH + 'static/icon/icon.funtion/icon.icns'))
    elif platform.system() == 'Linux' or platform.system() == 'Windows':
        app.setWindowIcon(QIcon(BASEPATH + 'static/icon/icon.funtion/icon0.png'))
    exe = Ashore()
    exe.show()
    splash.finish(exe)                  #关闭启动界面
    if len(sys.argv) != 1:
        exe.addNew(sys.argv[1:])
    app.fileOpenSignal.connect(exe.addNew)
    app.exec()
    del exe
    sys.exit()