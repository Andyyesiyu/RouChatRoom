# 聊天室使用方法

## 第一步 相关配置

首先安装本程序的配置环境python3.6，安装本文件需要的pyaudio包，opencv包，可以使用pip install的方式进行安装，对于opencv包可以执行以下命令：pip install opencv-python。安装无误后，在python界面中测试，若import pyaudio和import cv2都没有报错，则本次实验的环境就已经准备完全。

## 第二步 打开服务器
利用terminal进入项目主界面，使用python server_final.py --host 192.178.x.x （该ip为服务器的Ip地址），开启服务器，开启后，会打印出服务器正在运行的命令。

## 第三步 打开客户端
在另外的设备中，也进入项目所在文件解，使用python clinet_final.py的方式开启客户端。首先需要在UI最下方进行登陆，在多个用户登陆完成后，就可以使用软件进行聊天了。

## 第四步 其他功能
本软件的多用户聊天室功能已经基本健全，但是其他功能，例如文件传输、视频通话、语音传输虽然也可以使用，但是在发送大文件等情况下还有一定的bug，留待后续研究，详细使用方法请见视频演示。
