#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/04/01 16:56:04
@File    :   settingPage.py
@Software:   VSCode
@Author  :   PPPPAN 
@Version :   0.7.66
@Contact :   for_freedom_x64@live.com
'''

import sys, os, platform, subprocess, time

if __name__ == '__main__':
    if platform.system() == 'Darwin':
        print('当前系统为:MacOS')
        flag = input('make为程序包app 输入1 ,make为dmg发布 输入2 :\n')
        if flag == '1':
            print('......开始make程序为app......')
            os.system('rm -rf build/Ashore.MacOS.file')
            os.system('rm -rf dist/Ashore.MacOS.file')
            os.system('pyinstaller bale/Ashore.MacOS.file.spec')
            os.system('cp bale/Info.plist dist/Ashore.app/Contents/')
            os.system('mkdir dist/Ashore.MacOS.file')
            os.system('mkdir dist/Ashore.MacOS.file/Ashore')
            os.system('mv dist/Ashore.app dist/Ashore.MacOS.file/Ashore')
            os.system('mv dist/Ashore dist/Ashore.MacOS.file/Ashore')
            print('Ashore.app 打包完毕')
            cmd = 'open dist/Ashore.MacOS.file/Ashore/Ashore.app --reveal'
            subprocess.Popen([cmd],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif flag == '2':
            print('......开始make程序为dmg......')
            os.system('rm -rf build/Ashore.MacOS.dmg')
            os.system('rm -rf dist/Ashore.MacOS.dmg')
            os.system('defaults write com.apple.finder AppleShowAllFiles YES')
            os.system('killall Finder')
            os.system('pyinstaller bale/Ashore.MacOS.file.spec')
            os.system('cp bale/Info.plist dist/Ashore.app/Contents/')
            os.system('mkdir dist/Ashore.MacOS.dmg')
            os.system('mkdir dist/Ashore.MacOS.dmg/temp')
            os.system('mv dist/Ashore.app dist/Ashore.MacOS.dmg/temp')
            os.system('cp static/icon/icon.funtion/icon.icns dist/Ashore.MacOS.dmg')
            os.system('cp bale/dmg.png dist/Ashore.MacOS.dmg/temp/.background.png')
            os.system('rm dist/Ashore')
            os.chdir('dist/Ashore.MacOS.dmg') 
            os.system('ln -s /Applications temp')
            #使用temp文件夹制作dmg文件
            os.system('hdiutil create -srcfolder "temp" -size 50M -format UDRW -volname "Ashore Installer" "temp/Ashore.temp.dmg"')
            print('Created DMG: Ashore.temp.dmg')
            time.sleep(1)
            os.system('hdiutil attach "temp/Ashore.temp.dmg"')
            time.sleep(1)
            # 使用applescript设置一系列的窗口属性
            applescript = '''
            echo '
                tell application "Finder"
                    tell disk "Ashore Installer"
                        open
                        set current view of container window to icon view
                        set toolbar visible of container window to false
                        set statusbar visible of container window to false
                        set the bounds of container window to {300, 200, 1000, 660}
                        set viewOptions to the icon view options of container window
                        set arrangement of viewOptions to not arranged
                        set icon size of viewOptions to 128
                        set background picture of viewOptions to file ".background.png"
                        set position of item "Ashore.app" of container window to {130, 120}
                        set position of item "Applications" of container window to {390, 120}
                        set position of item ".background.png" of container window to {0, 0}
                        close
                        open
                        update without registering applications
                        delay 2
                    end tell
                end tell
                ' | osascript
                '''
            os.system(applescript)
            time.sleep(2)
            os.system('sync')
            # 设置映像图标
            os.system('cp icon.icns "/Volumes/Ashore Installer/.VolumeIcon.icns"')
            os.system('SetFile -c icnC "/Volumes/Ashore Installer/.VolumeIcon.icns"')
            os.system('SetFile -a C "/Volumes/Ashore Installer"')
            # 卸载
            time.sleep(5)
            os.system('hdiutil detach "/Volumes/Ashore Installer"')
            time.sleep(5)
            # 压缩映像并设置为只读
            print('Creating compressed image')
            os.system('hdiutil convert "temp/Ashore.temp.dmg" -format UDZO -imagekey zlib-level=9 -o "Ashore.dmg"')
            # 清除临时文件
            os.system('rm -r temp')
            os.system('rm icon.icns')
            os.system('defaults write com.apple.finder AppleShowAllFiles NO')
            os.system('killall Finder')
            print('Ashore.dmg 打包完毕')
            os.system('open Ashore.dmg --reveal')
        else:
            print('error')
    elif platform.system() == 'Linux':
        print('当前系统为:Linux')
        flag = input('make为单文件 输入1 ,make为文件夹 输入2 :\n')
        if flag == '1':
            print('......开始make为 单文件 程序......')
            os.system('rm -rf build/Ashore.Linux.file')
            os.system('rm -rf dist/Ashore.Linux.file')
            os.system('pyinstaller bale/Ashore.Linux.file.spec')
            os.system('mkdir dist/Ashore.Linux.file')
            os.system('mkdir dist/Ashore.Linux.file/Ashore')
            os.system('mv dist/Ashore dist/Ashore.Linux.file/Ashore')
            os.system('cp static/icon/icon.funtion/icon0.png dist/Ashore.Linux.file/Ashore/icon.png')
            os.system('cp bale/ashore.desktop dist/Ashore.Linux.file/Ashore')
            os.system('cp bale/make.Ashore.Linux.file.sh dist/Ashore.Linux.file/Ashore/make.sh')
            print('单文件 Ashore 打包完毕')
            cmd = 'nautilus dist/Ashore.Linux.file/Ashore/Ashore --select'
            subprocess.Popen([cmd],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif flag == '2':
            print('......开始make为 文件夹 程序......')
            os.system('rm -rf build/Ashore.Linux.folder')
            os.system('rm -rf dist/Ashore.Linux.folder')
            os.system('pyinstaller bale/Ashore.Linux.folder.spec')
            os.system('mkdir dist/Ashore.Linux.folder')
            os.system('mv -f dist/Ashore dist/Ashore.Linux.folder')
            os.system('cp static/icon/icon.funtion/icon0.png dist/Ashore.Linux.folder/Ashore/icon.png')
            os.system('cp bale/ashore.desktop dist/Ashore.Linux.folder')
            os.system('cp bale/make.Ashore.Linux.folder.sh dist/Ashore.Linux.folder/make.sh')
            print('文件夹 Ashore 打包完毕')
            cmd = 'nautilus dist/Ashore.Linux.folder/Ashore/Ashore --select'
            subprocess.Popen([cmd],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            print('error')
    elif platform.system() == 'Windows':
        print('当前系统为:Windows')