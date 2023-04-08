#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/03/25 15:06:43
@File    :   aria2Operate.py
@Software:   VSCode
@Author  :   PPPPAN 
@Version :   0.7.66
@Contact :   for_freedom_x64@live.com
'''

import urllib.request, urllib.error, urllib.parse, json, socket, sys, os ,platform , subprocess, time
from time import sleep

class Aria2Operate():
    totalNum = 1
    missions = {
        'active'    : {'913e29dd95f7313b' : {'filename' : 'aaa'}, '913e29dd95f731aa' : {'filename' : 'ccc'}},
        'waiting'   : {'913e294495f7313b' : {'filename' : 'bbb'}},
        'paused'    : {},
        'completed' : {},
        'error'     : {}
        }
    globalStatus = {
        'downloadSpeed'     : None,
        'numActive'         : None,     #正在下载及暂停的任务数量
        'numStopped'        : None,     #已完成及失败的任务数量
        'numStoppedTotal'   : None,     #所有任务？？？
        'numWaiting'        : None,     #排队等待的任务数量
        'uploadSpeed'       : None
        }
    missionStatusList = ['totalLength','completedLength','downloadSpeed']
    TIMEOUTSED = 1
    ARIA2METHOD = {
        'getGlobalStat'         : 'aria2.getGlobalStat',
        'add'                   : 'aria2.addUri',
        'addMetalink'           : 'aria2.addMetalink',
        'remove'                : 'aria2.remove',
        'removeResult'          : 'aria2.removeDownloadResult',
        'pause'                 : 'aria2.pause',
        'unpause'               : 'aria2.unpause',
        'pauseAll'              : 'aria2.pauseAll',
        'unpauseAll'            : 'aria2.unpauseAll',
        'tellActive'            : 'aria2.tellActive',
        'tellWaiting'           : 'aria2.tellWaiting',
        'tellStopped'           : 'aria2.tellStopped',
        # 'tellWaiting': 'aria2.tellWaiting',
        'getVersion'            : 'aria2.getVersion',
        'getFiles'              : 'aria2.getFiles',
        'tellStatus'            : 'aria2.tellStatus',
        'getGlobalOption'       : 'aria2.getGlobalOption',
        'changeGlobalOption'    : 'aria2.changeGlobalOption',
        'saveSession'           : 'aria2.saveSession',
        }

    ERRORLIST = {
         0  : "succeed",
        -1  : "HTTP Error",
        -2  : "URL Error",
        -3  : "WebSocket Error",
        -4  : 'Mission Not Found',
        -5  : 'Exception Error"',
        -6  : 'Unknow Error',
    }

    #搞清当前系统
    PlatformSystem = 'unknow'
    if platform.system() == 'Darwin':
        PlatformSystem = 'MacOS'
    elif platform.system() == 'Linux':
        PlatformSystem = 'Linux'
    elif platform.system() == 'Windows':
        PlatformSystem = 'Windows'

    def __init__(self, BASEPATH:str=None, QuitWithAria2:bool=False) -> None:
        self.isRelease = False
        # getattr 函数判断第一参数中是否含有第二参数这个属性：有则返回True，若没有：当第三参数为空时返回error，第三参数存在则返回第三参数
        if getattr(sys, 'frozen', False):
            self.isRelease = True
        #检验aria2是否安装
        if not self.isAria2Installed():
            # raise Exception('aria2 is not installed, please install it before.')
            self.myPrint('aria2 is not installed, please install it before.')
        #检验aria2是否已运行
        if not self.isAria2rpcRunning():
            #若未运行，则加载配置启动aria2
            # 传递参数运行基本目录来加载运行配置
            # cmd = self.loadConfig(BASEPATH)
            # #用系统命令行运行aria2c
            # subprocess.Popen([cmd],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # count = 0
            # while True:
            #     if self.isAria2rpcRunning():
            #         break
            #     else:
            #         count += 1
            #         time.sleep(3)
            #     if count == 5:
            #         raise Exception('aria2 RPC server started failure.')
            # self.myPrint('aria2 RPC server is started.')
            self.startAria2(BASEPATH)
        else:
            self.myPrint('aria2 RPC server is already running.')
        socket.setdefaulttimeout(0.003) 
        result = self.getGlobalStatus()
        #若失败就不断尝试链接
        while 'ResultError' in result:
            result = self.getGlobalStatus()
        self.QuitWithAria2 = QuitWithAria2
        self.myPrint(self.globalStatus)

    def addUrl(self, url:str, targetDir:str, rename:str=None, isTorrent:bool=None) -> dict:
        """添加单个下载任务
        :param url: str类型下载url
        :param targetDir: str类型下载路径
        :param rename: str类型重命名文件名
        :param isTorrent: bool类型是否为种子或bt链接
        :returns: 成功返回{}空字典,失败返回异常{'ResultError' : int}
        """
        jsonData = None
        if isTorrent == None:
            if url.startswith('magnet:?xt=urn:btih:') or url.endswith('.torrent'):
                isTorrent = True
            else:
                isTorrent = False
        if isTorrent == True:
            #种子或磁链
            params = [[url], {
                'dir' : targetDir,      # //下载根目录
                'referer' : '*'         # //referer 用来绕开部分防盗链机制 星号表示使用url作为referer
            }]
            jsonData = self.produceJson(method = self.ARIA2METHOD['add'], params = params)
        else:
            #非种子或磁链
            params = [[url], {
                'dir' : targetDir,     # //下载根目录
                'out' : rename,   # //目标文件名
                'referer' : '*' # //referer 用来绕开部分防盗链机制 星号表示使用url作为referer
            }]
            jsonData = self.produceJson(method = self.ARIA2METHOD['add'], params = params)
        addReslut = self.performan(data=jsonData)   #执行添加操作得到返回结果
        if 'ResultError' in addReslut:
            return addReslut
        else:
            return {}

    def addUrls(self, data:tuple=None, rename:str=None) -> None:
        """添加多个下载任务
        :param data传入元组类型,[0]为urls,格式为字典分为'urlList'和'torrentList'两个列表,[1]为下载目录
        :param name暂未设置,后续考虑加入为data[2]
        """
        urlList = data[0]['urlList']
        torrentList = data[0]['torrentList']
        targetDir = data[1]
        #添加普通url列表
        if len(urlList) > 0:
            if len(urlList) == 1:
                addResult = {'ResultError' : 0}
                while 'ResultError' in addResult:
                    addResult = self.addUrl(urlList[0], targetDir, rename)
            else:
                for url in urlList:
                    addResult = {'ResultError' : 0}
                    while 'ResultError' in addResult:
                        addResult = self.addUrl(url, targetDir)
        #添加磁链url列表
        if len(torrentList) > 0:
            for torrent in torrentList:
                addResult = {'ResultError' : 0}
                while 'ResultError' in addResult:
                    addResult = self.addUrl(torrent, targetDir)


    def addTorrent(self):
        """还未想好

        """

    def pause(self, gid:str) -> dict:
        jsonData = self.produceJson(method = self.ARIA2METHOD['pause'], params=[gid])
        result = self.performan(data=jsonData)   #执行添加操作得到返回结果。成功返回gid
        if result == gid:
            return {}       #设置成功返回空字典表示0
        else:
            return result   #设置失败返回带错误字典

    def unpause(self, gid:str) -> dict:
        jsonData = self.produceJson(method = self.ARIA2METHOD['unpause'], params=[gid])
        result = self.performan(data=jsonData)   #执行添加操作得到返回结果。成功返回gid
        if result == gid:
            return {}       #设置成功返回空字典表示0
        else:
            return result   #设置失败返回带错误字典

    def pauseAll(self) -> dict:
        jsonData = self.produceJson(method = self.ARIA2METHOD['pauseAll'])
        result = self.performan(data=jsonData)   #执行添加操作得到返回结果。成功返回'OK'
        if result == 'OK':
            return {}       #设置成功返回空字典表示0
        else:
            return result   #设置失败返回带错误字典

    def unpauseAll(self) -> dict:
        jsonData = self.produceJson(method = self.ARIA2METHOD['unpauseAll'])
        result = self.performan(data=jsonData)   #执行添加操作得到返回结果。成功返回'OK'
        if result == 'OK':
            return {}       #设置成功返回空字典表示0
        else:
            return result   #设置失败返回带错误字典

    def retry(self, gid:str) -> None:
        """重试就是先删除，再新建
        :param gid: 类型的下载任务gid
        :returns: 返回str类型下载任务url,或返回异常{'ResultError' : int}
        """
        missionResult = self.getMission(gid)#获取任务
        if 'ResultError' in missionResult:
            return missionResult    #任务不存在
        else:
            url = missionResult['url']
            isTorrent = missionResult['isTorrent']
            targetDir = missionResult['dir']
            delResult = self.delRemoveMission(gid, True)        #删除任务
            if 'ResultError' in delResult:
                return delResult
            else:
                addResult = {'ResultError' : 0}
                while 'ResultError' in addResult:
                    addResult = self.addUrl(url, targetDir, isTorrent)      #删除任务后添加下载任务

    def getGlobalStatus(self) -> dict:
        jsonData = self.produceJson(method = self.ARIA2METHOD['getGlobalStat'])
        globalResult = self.performan(data=jsonData)   #执行添加操作得到返回结果
        if 'ResultError' in globalResult:
            return globalResult
        else:
            self.globalStatus = globalResult
            return globalResult

    def getMissions(self) -> dict:
        #对active队列进行处理
        activeData = self.produceJson(method = self.ARIA2METHOD['tellActive'])
        activeResult = self.performan(data = activeData)   #执行添加操作得到返回结果
        self.totalNum = 0
        if 'ResultError' in activeResult:
            return activeResult
        else:
            activeGids = []
            for item in activeResult:
                gid = item['gid']
                activeGids.append(gid)
                self.setAttribute(item, gid, 'active') # 添加或修正mission字典中的任务信息
                # self.myPrint(item['status'])
                # self.myPrint(item['files'][0]['path'])
            self.removeSuperfluous(newGids = activeGids, status = 'active')     #删除多余任务
        #对waiting队列进行处理,分别进入waiting等待队列和paused暂停队列
        waitingData = self.produceJson(method = self.ARIA2METHOD['tellWaiting'],params=[0, int(self.globalStatus['numWaiting'])])
        waitingResult = self.performan(data = waitingData)   #执行添加操作得到返回结果
        if 'ResultError' in waitingResult:
            return waitingResult
        else:
            waitingGids = []
            pausedGids = []
            for item in waitingResult:
                gid = item['gid']
                if item['status'] == 'waiting':
                    waitingGids.append(gid)
                    self.setAttribute(item, gid, 'waiting')
                elif item['status'] == 'paused':
                    pausedGids.append(gid)
                    self.setAttribute(item, gid, 'paused')  # 添加或修正mission字典中的任务信息
                # self.myPrint(item['status'])
                # self.myPrint(item['files'][0]['path'])
            self.removeSuperfluous(newGids = waitingGids, status = 'waiting')     #删除多余任务
            self.removeSuperfluous(newGids = pausedGids, status = 'paused')     #删除多余任务
        #对stopped队列进行处理
        stoppedData = self.produceJson(method = self.ARIA2METHOD['tellStopped'],params=[0, int(self.globalStatus['numStopped'])])
        stoppedResult = self.performan(data = stoppedData)   #执行添加操作得到返回结果
        if 'ResultError' in stoppedResult:
            return stoppedResult
        else:
            completedGids = []
            errorGids = []
            for item in stoppedResult:
                gid = item['gid']
                #这里原作写错了吧，并没有加complete过去式的ed
                if item['status'] == 'complete':
                    completedGids.append(gid)
                    self.setAttribute(item, gid, 'completed')
                elif item['status'] == 'error':
                    errorGids.append(gid)
                    self.setAttribute(item, gid, 'error')   # 添加或修正mission字典中的任务信息
                # self.myPrint(item['status'])
                # self.myPrint(item['files'][0]['path'])
            self.removeSuperfluous(newGids = completedGids, status = 'completed')     #删除多余任务
            self.removeSuperfluous(newGids = errorGids, status = 'error')     #删除多余任务
        # print(len(self.missions['active'])+len(self.missions['waiting'])+len(self.missions['paused'])+len(self.missions['completed'])+len(self.missions['error']))
        return self.missions

    def getMissionFromAria2(self, gid:str) -> dict:
        jsonData = self.produceJson(method = self.ARIA2METHOD['getFiles'], params=[gid])
        result = self.performan(data=jsonData)   #执行添加操作得到返回结果
        return result

    def updateMissionsFromAria2(self, neededStatus:list) -> dict:
        #对于不同页面有不同neddedStatus需要，精简获取信息加速程序运行，属于信息内容小更新
        for status in neededStatus:
            for gid in self.missions[status]:
                jsonData = self.produceJson(method = self.ARIA2METHOD['tellStatus'], params=[gid, self.missionStatusList])
                result = self.performan(data=jsonData)   #执行添加操作得到返回结果
                if 'ResultError' in result:
                    return result
                for item in self.missionStatusList:
                    #按照missionStatusList的内容['totalLength','completedLength','downloadSpeed']逐一更新状态
                    self.missions[status][gid][item] = result[item]
        return self.missions

    def getMission(self, gid:str) -> dict:
        """获取该任务信息,包括 filename、url、dir、isTorrent、totalLength、completedLength、downloadSpeed、uploadSpeed
        :param gid: 类型的下载任务gid
        :returns: 返回dict类型下载任务信息字典,或返回异常{'ResultError' : int}
        """
        for status,missionList in self.missions.items():
            if gid in missionList:
                mission = missionList[gid]
                mission['status'] = status
                return mission
        return {'ResultError' : -4}

    def getAria2Version(self) -> str:
        jsonData = self.produceJson(method = self.ARIA2METHOD['getVersion'])
        result = self.performan(data=jsonData)   #执行添加操作得到返回结果
        if 'version' in result:
            return result['version']
        else:       #先回复一个好久不更新版本代替下
            return '1.36.0'

    def seekFileName(self, item:dict, bittorrent:bool) -> str:
        #因bt数据结构不同，故分开讨论
        filename = ''
        if bittorrent == False:
            #若下载地址为常规链接
            if 'path' in item.keys(): 
                #若有路径可直接使用
                if item['path'] != '':
                    filename = self.splitUrlToName(item['path'])
                else:
                    self.myPrint(item)
            elif 'uris' in item['files'][0].keys():
                #从uris参数集中查找
                if item['files'][0]['path'] != '':
                    filename = self.splitUrlToName(item['files'][0]['path'])
                elif item['files'][0]['uris'][0]['uri'] != None:
                    filename = self.splitUrlToName(item['files'][0]['uris'][0]['uri'])
                else:
                    self.myPrint(item.keys())
            else:
                self.myPrint(item)
            # 将url链接形式的文件名进行解码
            filename = urllib.parse.unquote(filename)
            self.totalNum += 1
            #显示所有任务
            # self.myPrint(str(self.totalNum) + ' ' + filename)
        elif bittorrent == True:
            if 'info' in item['bittorrent'].keys():
                if item['bittorrent']['info']['name'] != None:
                    filename = item['bittorrent']['info']['name']
                else:
                    self.myPrint(str(self.totalNum) +filename)
            elif item['files'][0]['path'] != None:
                filename = '[BT] ' + self.splitUrlToName(item['files'][0]['path'])
            else:
                self.myPrint(item.keys())
            self.totalNum += 1
            #显示所有任务
            # self.myPrint(str(self.totalNum) + ' ' + filename)
        else:
            self.myPrint(item.keys())
        return filename

    def splitUrlToName(self, url:str) -> str:
        #从url中提取文件名
        string = url.split('?', 1)[0]
        string = string.split('/')[-1]
        string = string.split('[METADATA]')[-1]
        return string

    def setAttribute(self, item:dict, gid:str, status:str) -> None: # 添加或修正mission字典中的任务信息
        # 获取各项属性
        if 'bittorrent' not in item.keys():
            #若下载地址为常规链接
            url = item['files'][0]['uris'][0]['uri']
            filename = self.seekFileName(item=item, bittorrent=False)
            isTorrent = False
        else:
            #若下载地址为BT链接
            url = 'magnet:?xt=urn:btih:' + item['infoHash']
            filename = self.seekFileName(item=item, bittorrent=True)
            isTorrent = True
        # 设置进任务mission字典
        self.missions[status][gid] = {
            'totalLength'       : int(item['totalLength']),
            'completedLength'   : int(item['completedLength']),
            'dir'               : item['dir'],
            'url'               : url,
            'downloadSpeed'     : int(item['downloadSpeed']),
            'uploadSpeed'       : int(item['uploadSpeed']),
            'filename'          : filename,
            'isTorrent'         : isTorrent,
            }

    def removeSuperfluous(self, newGids:set, status:str) -> None:
        #比较新gid列表中已经删除、完成的任务，但原始列表仍存在的，进行删除
        removeGids = set(self.missions[status].keys()).difference(set(newGids))
        for gid in removeGids:
            del self.missions[status][gid]

    def getUrl(self, gid:str) -> dict:
        """通过任务gid获取下载地址url
        :returns: 返回str类型下载任务url,或返回异常{'ResultError' : int}
        """
        mission = self.getMission(gid)
        if 'ResultError' in mission:
            #若未找到所给gid的任务，返回含错误代码字典{'ResultError' : -4}
            return mission
        else:
            return {'url' : mission['url']}

    def delRemoveMission(self, gid:str, delFile:bool=False) -> dict:
        """从任务列表中移除任务&彻底删除任务(包括下载文件)两个功能
        :param gid: str类型任务gid
        :param delFile: bool类型标志符:False列表中移除任务不删文件,True彻底删除
        :returns: 成功返回{}空字典,失败返回异常{'ResultError' : int}
        """
        mission = self.getMission(gid)
        if 'ResultError' in mission:
            #若未找到所给gid的任务，返回含错误代码字典{'ResultError' : -4}
            return mission
        else:
            #找到任务开始处理
            if mission['status'] == 'active' or mission['status'] == 'waiting' or mission['status'] == 'paused':
                #若任务进行中，则先用方法使任务进入remove列表掉再删除
                jsonData = self.produceJson(method = self.ARIA2METHOD['remove'], params=[gid])
                result = self.performan(data=jsonData)   #执行添加操作得到返回结果
                if 'ResultError' in result:
                    return result       #若报错直接返回错误
                # 这段有点迷惑 elif mission['status'] == 'completed' or mission['status'] == 'error' or mission['status'] == 'removed':这段有点迷惑
            time.sleep(0.1)

            # 具体删除任务removes a completed/error/removed download
            jsonData = self.produceJson(method = self.ARIA2METHOD['removeResult'], params=[gid])
            result = self.performan(data=jsonData)   #执行添加操作得到返回结果
            if 'ResultError' in result:
                return result       #若报错直接返回错误

            # 删除文件，看文件路径print('\033[1;44m file name: \033[0m' + mission['dir'] + '/' + mission['filename'])
            file = mission['dir'] + '/' + mission['filename']
            if file != '':
                #若命令文件名为空，避免出现rm —rf致命问题
                filecmd = 'rm -rf ' + file
                aria2cmd = filecmd + '.aria2'
                #无论下载文件是否删除都先删除aria2记录文件
                subprocess.Popen([aria2cmd],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if delFile == True:
                    #若需要删除下载的文件
                    subprocess.Popen([filecmd],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return {} #处理完毕返回空字典表示0
            else:
                #若命令文件名为空返回错误代码-5
                return {'ResultError' : -5}

    def openFileDir(self, gid:str) -> dict:
        mission = self.getMission(gid)
        if 'ResultError' in mission:
            #若未找到所给gid的任务，返回含错误代码字典{'ResultError' : -4}
            return mission
        else:
            platformSystem = self.PlatformSystem
            filePath = mission['dir'] + '/' + mission['filename']
            cmd = ''
            if platformSystem == 'MacOS':           # MacOS
                cmd = 'open "' + filePath + '" --reveal'
            elif platformSystem == 'Linux':         # Linux
                #先检测文件管理器nautilus是否存在
                cmd = 'which nautilus'
                isNautilus = subprocess.Popen([cmd],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,encoding='utf-8')
                if isNautilus.communicate()[0] != '':
                    #若返回结果非空，则nautilus存在
                    cmd = 'nautilus "' + filePath + '" --select'
                else:
                    #若返回结果空，返回文件夹路径使用pyqt通用方法
                    return {'dir' : mission['dir']}
            elif platformSystem == 'Windows':       # Windows
                cmd = 'explorer /select,"' + filePath + '"'
            else:           #防止其他情况
                return {'dir' : mission['dir']}
            subprocess.Popen([cmd],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return {} #返回空字典表示0成功

    def getFilePath(self, gid:str) -> dict:
        mission = self.getMission(gid)
        if 'ResultError' in mission:
            #若未找到任务，返回含错误代码-4的字典
            return mission
        else:
            #若存在返回目录+文件名
            return {'filePath' : mission['dir'] + '/' + mission['filename']}

    def getGlobalConfig(self) -> dict:
        jsonData = self.produceJson(method = self.ARIA2METHOD['getGlobalOption'])
        result = self.performan(data=jsonData)   #执行添加操作得到返回结果
        return result

    def setGlobalConfig(self, conf:dict=None) -> dict:
        jsonData = self.produceJson(method = self.ARIA2METHOD['changeGlobalOption'], params = [conf])
        result = self.performan(data=jsonData)   #执行添加操作得到返回结果
        if result != 'OK':
            return {}       #设置成功返回空字典表示0
        else:
            return result   #设置失败返回带错误字典

    def produceJson(self, method:str, params:list=[]) -> str:
        #生成json格式数据
        data = json.dumps({'jsonrpc' : '2.0', 'id' : 'qwer', 'method' : method, 'params' : params})
        self.myPrint(data)
        return data

    def performan(self, host="http://localhost", port=6801, secret="", data:str='{}', numRetry:int=7) -> dict:
        url = host + ':' + str(port) + '/jsonrpc'
        count = 0
        sleepSecond = 0.5
        result = 0
        while count < numRetry:
            try:
                jsonResponse = urllib.request.urlopen(url, data.encode(encoding='UTF8'), timeout=self.TIMEOUTSED)
                dictResponse = json.loads(jsonResponse.read().decode())
                result = dictResponse['result']
                #通信成功直接将cout赋值跳过循环
                count = numRetry
            except urllib.error.HTTPError as e:
                count += 1
                self.myPrint('\033[0;37;41m 报错啦!!!!!! \033[0m')
                if hasattr(e, 'code'):
                    self.myPrint(e.code, end='\t')
                if hasattr(e, 'reason'):
                    self.myPrint(e.reason)
                result = {'ResultError' : -1}
                time.sleep(sleepSecond)
            except urllib.error.URLError as e:
                count += 1
                self.myPrint('\033[0;37;41m 报错啦!!!!!! \033[0m')
                if hasattr(e, 'code'):
                    self.myPrint(e.code, end='\t')
                if hasattr(e, 'reason'):
                    self.myPrint(e.reason)
                result = {'ResultError' : -2}
                time.sleep(sleepSecond)
            except socket.error as e:
                count += 1
                self.myPrint('\033[0;37;41m 报错啦!!!!!! \033[0m')
                self.myPrint('Socket\t' + str(e))
                result = {'ResultError' : -3}
                #若超时返回‘timed out’,被其他程序挤掉返回’[Errno 54] Connection reset by peer‘
                time.sleep(sleepSecond)
            except Exception as e:
                #未知异常代码-5，-4代码为not found
                count += 1
                self.myPrint('\033[0;37;41m 报错啦!!!!!! \033[0m')
                self.myPrint(str(e))
                result = {'ResultError' : -5}
                time.sleep(sleepSecond)
        return result

    def loadConfig(self, BASEPATH:str=None) -> str:
        # os.system('aria2c --conf-path="/Users/panzk/.config/aria2/aria2.conf" -D')为原始命令，但发布软件运行后的目录有动态变化，故用下面方法找出运行目录及配置目录
        #判断配置文件夹及配置文件是否存在
        # BASEPATH = ''
        # if getattr(sys, 'frozen', False):
        #     #判断是否为发布状态，利用系统方法找到运行目录
        #     BASEPATH = sys._MEIPASS + '/'
        if not os.path.exists(os.path.expanduser('~/.config/ashore')):
            #查看配置目录是否存在，若不存在则复制一份到默认目录
            os.system('mkdir ~/.config/ashore')
            os.system('cp ' + BASEPATH + 'config/aria2.conf ~/.config/ashore/aria2.conf')
            os.system('cp ' + BASEPATH + 'config/aria2.session ~/.config/ashore/aria2.session')
        if not os.path.exists(os.path.expanduser('~/.config/ashore/aria2.conf')):
            #查看配置文件是否还在，若不在复制一份到配置目录
            os.system('cp ' + BASEPATH + 'config/aria2.conf ~/.config/ashore/aria2.conf')
        if not os.path.exists(os.path.expanduser('~/.config/ashore/aria2.session')):
            os.system('cp ' + BASEPATH + 'config/aria2.session ~/.config/ashore/aria2.session')
        cmd = ''
        if os.path.exists('/usr/bin/aria2c'):
            cmd = '/usr/bin/aria2c --conf-path="' + os.path.expanduser('~') + '/.config/ashore/aria2.conf" -D'
            self.myPrint(cmd)
            return cmd
        elif os.path.exists('/usr/local/bin/aria2c'):
            cmd = '/usr/local/bin/aria2c --conf-path="' + os.path.expanduser('~') + '/.config/ashore/aria2.conf" -D'
            self.myPrint(cmd)
            return cmd
        else:
            exit(2)

    def isAria2Installed(self) -> bool:
        for cmdpath in os.environ['PATH'].split(':'):
            if os.path.isdir(cmdpath) and 'aria2c' in os.listdir(cmdpath):
                return True

    def isAria2rpcRunning(self) -> bool:
        pgrep_process = subprocess.Popen('pgrep -l aria2', shell=True, stdout=subprocess.PIPE)
        if pgrep_process.stdout.readline() == b'':
            return False
        else:
            return True

    def myPrint(self, data, end=None):
        # getattr 函数判断第一参数中是否含有第二参数这个属性：有则返回True，若没有：当第三参数为空时返回error，第三参数存在则返回第三参数
        if not self.isRelease:
            #当程序处于coding阶段时允许输出，当为release时禁止输出
                print(data, end=end)

    def saveSession(self):
        jsonData = self.produceJson(method = self.ARIA2METHOD['saveSession'])
        saveResult = self.performan(data=jsonData)   #执行添加操作得到返回结果
        if saveResult == 'OK':
            return {}       #设置成功返回空字典表示0
        else:
            return saveResult   #设置失败返回带错误字典

    def startAria2(self, BASEPATH:str) -> None:
        # 传递参数运行基本目录来加载运行配置
        cmd = self.loadConfig(BASEPATH)
        #用系统命令行运行aria2c
        subprocess.Popen([cmd],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        count = 0
        while True:
            if self.isAria2rpcRunning():
                break
            else:
                count += 1
                time.sleep(3)
            if count == 5:
                raise Exception('aria2 RPC server started failure.')
        self.myPrint('aria2 RPC server is started.')

    def restartAria2(self, BASEPATH:str):
        self.saveSession()
        if self.killAria2():
            # 传递参数运行基本目录来加载运行配置
            self.startAria2(BASEPATH)

    def killAria2(self) -> bool:
        killAria2Cmd = 'pkill -f aria2c'
        isQuit = subprocess.Popen([killAria2Cmd],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
        if isQuit.communicate()[0] == '':
            return True
        else:
            return False

    def mainKillAria2(self) -> bool:
        """结束主程序时运行,通过self.QuitWithAria2自行判断是否在关闭程序时结束aria2
        """
        if self.QuitWithAria2:
            return self.killAria2()
        else:
            return True


if __name__ == '__main__':
    aria2 = Aria2Operate()
    # aria2.addUrls(urls=[
    #     'https://xt2-ddbxs-com.supergslb.com/2022/win10/02/GHOST_WIN10_X64_V2022.03A.iso?auth_key=1647751253-0-0-fa0d22f1a999bac48a84b0dce65dfaa7',
    #     'https://cdn.shemaleleaks.com/content/03/Pack_000/vicats/video_vicats_nude_leaks_shemaleleaks.com_001.mp4?_=2'
    #     ,'magnet:?xt=urn:btih:99C82BB73505A3C0B453F9FA0E881D6E5A32A0C1&dn=ubuntu-22.10-desktop-amd64.iso'
    #     ,'https://www.btnull.org/down/be08CkdzrOSIR_C3D9AC2udNgjtOU-U_FBzuf5r1EtwXqsutaDWOMwW1MFtD3sl9A2m_LIR69NSrjDd2Z2rhRSmR5vDB-omPDgp7lAVm5IfJjcFfGRibQg5a_SgUaOk28ifJ1iIwPUTLrHw4owRTGlLcvqeDYzjbvTs-18PBz6ghLdssebIObya2hC9i/'])
    # aria2.addUrl(url='https://cdn.shemaleleaks.com/content/03/Pack_000/vicats/video_vicats_nude_leaks_shemaleleaks.com_001.mp4?_=2')
    print(aria2.getAria2Version())
    for i in range(1,30):
        aria2.getMissions()
        a = aria2.getMission('c8ce4adfe497a09e')
        bb= aria2.getMissionFromAria2('c8ce4adfe497a09e')
        filename= a['filename']
        print(urllib.parse.unquote(filename))
        print('第%d次完成' % i)
        sleep(2)

    # aria2.updateMissionsFromAria2(['active'])
    # path = aria2.getMissionFromAria2('1a4e6e90cd8ec62e')
    # jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
    #                   'method':'aria2.addUri',
    #                   'params':[['https://xt2-ddbxs-com.supergslb.com/2022/win10/02/GHOST_WIN10_X64_V2022.03A.iso?auth_key=1647751253-0-0-fa0d22f1a999bac48a84b0dce65dfaa7']]})