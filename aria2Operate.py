#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2022/03/20 10:22:15
@File    :   aria2Operate.py
@Software:   VSCode
@Author  :   PPPPAN 
@Version :   0.1.80
@Contact :   for_freedom_x64@live.com
'''

import os, sys, aria2p, subprocess
from time import sleep

TESTURL = 'https://xt2-ddbxs-com.supergslb.com/2022/win10/02/GHOST_WIN10_X64_V2022.03A.iso?auth_key=1647751253-0-0-fa0d22f1a999bac48a84b0dce65dfaa7'

class Aria2Operate():
    def __init__(self):
        # os.system('aria2c --conf-path="/Users/panzk/.config/aria2/aria2.conf" -D')
        #判断配置文件夹及配置文件是否存在
        BASEPATH = ''
        if getattr(sys, 'frozen', False):
            BASEPATH = sys._MEIPASS + '/'
        if not os.path.exists(os.path.expanduser('~/.config/ashore')):
            os.system('mkdir ~/.config/ashore')
            os.system('cp ' + BASEPATH + 'config/aria2.conf ~/.config/ashore/aria2.conf')
            os.system('cp ' + BASEPATH + 'config/aria2.session ~/.config/ashore/aria2.session')
        if not os.path.exists(os.path.expanduser('~/.config/ashore/aria2.conf')):
            os.system('cp ' + BASEPATH + 'config/aria2.conf ~/.config/ashore/aria2.conf')
        if not os.path.exists(os.path.expanduser('~/.config/ashore/aria2.session')):
            os.system('cp ' + BASEPATH + 'config/aria2.session ~/.config/ashore/aria2.session')
        cmd = ''
        if os.path.exists('/usr/bin/aria2c'):
            cmd = '/usr/bin/aria2c --conf-path="' + os.path.expanduser('~') + '/.config/ashore/aria2.conf" -D'
        elif os.path.exists('/usr/local/bin/aria2c'):
            cmd = '/usr/local/bin/aria2c --conf-path="' + os.path.expanduser('~') + '/.config/ashore/aria2.conf" -D'
        else:
            exit(2)
        subprocess.Popen(cmd,shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # os.system('aria2c --conf-path="' + os.path.expanduser('~') +'/.config/ashore/aria2.conf" -D')
        # print('aria2c --conf-path="' + os.path.expanduser('~') +'/.config/ashore/aria2.conf" -D')
        self.aria2 = aria2p.API(aria2p.Client(host="http://localhost",port=6801,secret=""))

    def getDownloading(self):
        downloads = self.aria2.get_downloads()
        return downloads
        for download in downloads:
            print('文件名%s,状态%s,速度%s,gid%s' % (download.name, download.status, download.download_speed_string, download.gid))

    def addDownloads(self, data:tuple):
        urls = data[0]
        path = data[1]
        for url in urls:
            self.aria2.add(url, {'dir': path})
    
    def getObjects(self, gids:list[str]) -> list:   #通过gid号得到aria2下载对象downloaddObject
        temp = []
        for gid in gids:
            temp.append(self.aria2.get_download(gid))
        return temp

    def resumeDownloads(self, gids: list[str]):
        self.aria2.resume(self.getObjects(gids))

    def pauseDownloads(self, gids: list[str]):
        self.aria2.pause(self.getObjects(gids))
    
    def retryDownloads(self, gids: list[str]):
        self.aria2.retry_downloads(self.getObjects(gids))

    def getDir(self, gid: str) -> str:
        temp = self.aria2.get_download(gid)
        option = self.aria2.get_options([temp])[0]
        return option.dir

    def getFilePath(self, gid: str) -> str:
        temp = self.aria2.get_download(gid)
        option = self.aria2.get_options([temp])[0]
        filePath = option.dir + '/' + temp.name
        return filePath
    
    def removeDelDownloads(self, gids: list[str],  delFiles: bool = False):
        temp = self.getObjects(gids)
        self.aria2.remove(temp, force = True, files=delFiles, clean=True)

    def getGlobalConfig(self) -> dict:
        conf = self.aria2.get_global_options().get_struct()
        return conf
    
    def setGlobalConfig(self, conf:dict):
        f = self.aria2.set_global_options(conf)
    
    # def getConfigPath(self):
    #     dic = self.getGlobalConfig()
    #     return dic['conf-path']

    def __del__(self):
        os.system('pkill -f aria2c')
        # print("调用__del__() 销毁对象，释放其空间")

if __name__ == '__main__':
    aria2Operate = Aria2Operate()
    print(111)
    print(aria2Operate.aria2.get_global_options().get_struct()['allow-overwrite'])
    sleep(10)
    print(222)
    # aria2Operate.addDownload(TESTURL)
    aria2Operate.getDownloading()