@echo off
NODE_PATH="vendor/node/win32"
NODE="%NODE_PATH%/bin/node.exe"

"%NODE%" "%~dp0/build.js"