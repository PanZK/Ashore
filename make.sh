#! /bin/zsh
APP_NAME="Ashore"
echo "对${APP_NAME}进行打包"
pyinstaller -F ${APP_NAME}.spec
cp Info.plist dist/${APP_NAME}.app/Contents/
echo "${APP_NAME}打包完毕"