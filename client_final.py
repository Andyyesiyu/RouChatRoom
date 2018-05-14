# -*- coding: utf-8 -*-
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import socket
import time
import threading
import json
import os
import argparse
import audioFeatureTest
from openav import openav
from PIL import Image, ImageTk


# monitor chatroom，此为1号客户端，要视频聊天另一方需要2号客户端，使用opencv2，start（）的ip地址改为server_ip
class window:
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 初始化socket
        self.__nickname = None
        '''''创建分区'''
        f_msglist = tkinter.Frame(height=300, width=300)  # 创建<消息列表分区 >
        f_msgsend = tkinter.Frame(height=200, width=300)  # 创建<发送消息分区 >
        f_floor = tkinter.Frame(height=50, width=300)  # 创建<按钮分区>
        f_floor_ip = tkinter.Frame(height=50, width=300)  # 创建<按钮分区>
        f_right = tkinter.Frame(height=600, width=800)  # 创建<图片分区>
        '''''创建控件'''
        self.txt_msglist = tkinter.Text(
            f_msglist, height=30, width=80)  # 消息列表分区中创建文本控件
        self.txt_msglist.tag_config('green', foreground='blue')  # 消息列表分区中创建标签
        self.listbar = tkinter.Scrollbar(f_msglist)  # 设置滚动条
        self.txt_msgsend = tkinter.Text(
            f_msgsend, height=10, width=83)  # 发送消息分区中创建文本控件
        self.txt_msgsend.bind('<KeyPress-Up>',
                              self.msgsendEvent)  # 发送消息分区中，绑定‘UP’键与消息发送。
        '''''txt_right = Text(f_right) #图片显示分区创建文本控件'''
        self.loginprompt = tkinter.Text(f_floor, height=1, width=10)  # 输入用户名
        self.button_login = tkinter.Button(f_floor, text='登录', command=lambda: self.do_login(args=self.loginprompt.get('0.0', tkinter.END)))  # 分区中创建登录按钮并绑定登录函数
        self.button_send = tkinter.Button(f_floor, text='发送（快捷键：↑）', command=lambda: self.do_send(args=self.txt_msgsend.get('0.0', tkinter.END)))  # 按钮分区中创建按钮并绑定发送消息函数
        self.button_img = tkinter.Button(f_floor, text='发送图片', command=lambda: self.do_send_img(args=tkinter.filedialog.askopenfilename(filetypes=[('JPG', '*.jpg'), ('BMP', '*.bmp'), ('GIF', '*.gif'), ('PNG', '*.png')])))
        self.button_file = tkinter.Button(f_floor, text='文件极速秒传', command=lambda: self.do_send_file(args=tkinter.filedialog.askopenfilename()))
        self.button_audio = tkinter.Button(f_floor, text='发送语音消息', command=lambda: self.do_send_audio())
        self.ipmsg = tkinter.Label(f_floor_ip, text='请输入视频聊天目标ip地址：')
        self.ipprompt = tkinter.Text(f_floor_ip, height=1, width=15)
        self.button_av = tkinter.Button(
            f_floor_ip, text='视频聊天',
            command=lambda: self.avstart())  # 分区中创建视频聊天按钮并绑定函数
        img = Image.open(os.path.join(
            os.getcwd(), 'background.jpg'))  # 非gif要用PIL模块的PhotoImage打开
        resizedimg = img.resize((400, 300))  # 调整图像大小
        photo = ImageTk.PhotoImage(resizedimg)  # 非gif要用PIL模块的PhotoImage打开
        self.label = tkinter.Label(
            f_right, image=photo, padx=5, pady=5)  # 右侧分区中添加标签（绑定图片）
        self.label.image = photo
        self.label_img = tkinter.Label(
            f_right)  # 表情包现实区域，初始空白

        '''''组件关联'''
        self.listbar.config(command=self.txt_msglist.yview)  # 滚动条纵向贴入信息框
        self.txt_msglist.config(yscrollcommand=self.listbar.set)  # 设置滚动条的参数

        '''''分区布局'''
        f_msglist.grid(row=0, column=0)  # 消息列表分区
        f_msgsend.grid(row=1, column=0)  # 发送消息分区
        f_floor.grid(row=2, column=0)  # 按钮分区
        f_floor_ip.grid(row=3, column=0)  # 语音视频目标输入分区
        f_right.grid(row=0, column=1, rowspan=4)  # 图片显示分区
        self.txt_msglist.grid()  # 消息列表文本控件加载
        self.txt_msgsend.grid()  # 消息发送文本控件加载
        self.loginprompt.grid(row=0, column=0, sticky=tkinter.W)  # 用户名输入加载
        self.button_login.grid(row=0, column=1, sticky=tkinter.W)  # 取消按钮控件加载
        self.button_send.grid(row=0, column=2, sticky=tkinter.W)  # 发送按钮控件加载
        self.button_img.grid(row=0, column=3, sticky=tkinter.W)   # 发送图片按钮加载
        self.button_audio.grid(row=0, column=4, sticky=tkinter.W)  # 发送语音按钮加载
        self.button_file.grid(row=0, column=5, sticky=tkinter.W)  # 发送文件按钮加载

        self.ipmsg.grid(row=0, column=1, sticky=tkinter.W)  # 提示信息加载
        self.ipprompt.grid(row=0, column=2)  # ip输入框加载
        self.button_av.grid(row=0, column=3, sticky=tkinter.W)  # 视频按钮控件加载
        self.label.grid(row=0, column=0, rowspan=2)  # 右侧分区加载标签控件(图片)，待调整大小
        self.label_img.grid(row=2, column=0, rowspan=2)
        self.listbar.grid(column=1, row=0, sticky='NS')  # 安滚动条，待搞
        self.txt_msglist.insert(
            tkinter.END,
            '欢迎来到网络创新第一队局域网聊天室v4——客户端基于python原生GUI库tkinter\n采用socket服务器广播方案，通过多线程实现局域网登陆功能、群聊功能、视频语言聊天功能。(opencv/pyaudio)、极速文件传输功能\n\n特别鸣谢：\n叶思宇(队长，总体架构设计，服务器端开发，文件模块开发）\n沈恺飞（客户端GUI开发实现，视频模块开发，测试）\n陈向可（视频模块设计，测试）\n周奕文（超级美工，测试）\n顾端东（代码学习顾问）\n\n使用须知：\n请务必先在底部输入用户名登录\n',
            'green')  # 默认欢迎语

    def msgsendEvent(self, event):
        if event.keysym == 'Up':
            self.do_send(args=self.txt_msgsend.get('0.0', tkinter.END))

    def __receive_message_thread(self):
        """
        接受消息(文件)线程
        """
        while True:
            # noinspection PyBroadException
            try:
                buffer = self.__socket.recv(1024).decode()
                obj = json.loads(buffer)
                if obj['type'] == 'text':
                    msg = str(obj['sender_nickname']) + '(' + str(
                        obj['sender_id']) + ')' + '[' + time.strftime(
                            '%Y-%m-%d %H:%M:%S', time.localtime()) + ']' + '\n'
                    self.txt_msglist.insert(tkinter.END, msg, 'green')  # 添加时间
                    self.txt_msglist.insert(tkinter.END,
                                            obj['message'])  # 接受消息，添加文本到消息列表
                if obj['type'] == 'file':
                    answer = tkinter.messagebox.askquestion(
                        title='文件接受',
                        message='收到文件 ' + obj['filename'] + '文件大小为 ' +
                        str(obj['message']) + 'B。\n' + '是否接收？')
                    if answer == 'yes':
                        self.do_receive_file(obj['filename'], obj['message'])
                    else:
                        self.txt_msglist.insert(tkinter.END, '您已经拒绝接收文件\n',
                                                'red')
                if obj['type'] == 'img':
                    self.txt_msglist.insert(tkinter.END, str(obj['sender_nickname']) + '(' + str(
                        obj['sender_id']) + ')' + '[' + time.strftime(
                            '%Y-%m-%d %H:%M:%S', time.localtime()) + ']' + '\n')
                    self.txt_msglist.insert(tkinter.END, '发来表情包，请看右方\n')
                    self.do_receive_img(obj['filename'], obj['message'])
                if obj['type'] == 'audio':
                    answer = tkinter.messagebox.askquestion(
                        title='接收到音频',
                        message='收到来自' + str(obj['sender_nickname']) +
                        '的语音\n' + '是否收听？')
                    if answer == 'yes':
                        self.do_receive_audio(obj['message'])
                    else:
                        self.txt_msglist.insert(tkinter.END, '您已经拒绝接收语音\n',
                                                'red')
                self.txt_msglist.see(tkinter.END)  # 保持显示最底部
            except Exception:
                self.txt_msglist.insert(tkinter.END, '[Client] 无法从服务器获取数据\n',
                                        'green')

    def __send_message_thread(self, message):
        """
        发送消息线程
        :param message: 消息内容
        """
        self.__socket.send(
            json.dumps({
                'type': 'broadcast',
                'sender_id': self.__id,
                'message': message
            }).encode())

    def __send_file_thread(self, filelocation):
        """
        发送文件线程
        :param message: 文件内容
        """
        self.__socket.send(
            json.dumps({
                'type':
                'file',
                'sender_id':
                self.__id,
                'message':
                os.stat(filelocation).st_size,
                'filename':
                filelocation.replace('/', ' ').replace('\\', ' ').split()[-1]
            }).encode())
        __file = open(filelocation, 'rb')
        while True:
            filedata = __file.read(1024)
            print(len(filedata))
            if not filedata:
                break
            self.__socket.send(filedata)
        __file.close()
        print('线程内发送结束')

    def __send_img_thread(self, imglocation):
        """
        发送图片线程
        :param imglocation: 发送图片地址
        """
        self.__socket.send(json.dumps({
            'type': 'img',
            'sender_id': self.__id,
            'message': os.stat(imglocation).st_size,
            'imgname': imglocation.replace('/', ' ').replace('\\', ' ').split()[-1]
        }).encode())
        __img = open(imglocation, 'rb')
        while True:
            imgdata = __img.read(1024)
            if not imgdata:
                break
            self.__socket.send(imgdata)
        __img.close()
        print('线程内图片发送完毕')

    def __send_audio_thread(self, audio_data):
        """
        发送音频线程
        :param audio_data: 音频文件分包后的数组
        """
        print('开始发送语音')
        self.__socket.send(json.dumps({
            'type': 'audio',
            'sender_id': self.__id,
            'message': os.stat(audio_data).st_size
            # 'audioslicesize': sys.getsizeof(audio_data[1])
        }).encode())
        __audio = open('temp.wav', 'rb')
        while True:
            audata = __audio.read(1024)
            if not audata:
                break
            self.__socket.send(audata)
        __audio.close()
        print('线程内音频发送完毕')

    def __receive_img_thread(self, imgname, imgsize):
        num = imgsize / 1024.0
        if num != int(num):
            num = int(num) + 1
        else:
            num = int(num)
        new_img_name = imgname+'_temp'
        new_img = open(os.path.join(os.getcwd(), new_img_name),
                       'wb')  # 处理文件名，进行存储
        for i in range(num):
            buffer = self.__socket.recv(1024)
            new_img.write(buffer)
        new_img.close()
        img = Image.open(os.path.join(
            os.getcwd(), new_img_name))  # 非gif要用PIL模块的PhotoImage打开
        ratio = min(400 / img.size[0], 300 / img.size[1])
        wid, hei = int(img.size[0] * ratio), int(img.size[1] * ratio)
        resizedimg = img.resize((wid, hei))
        photo = ImageTk.PhotoImage(resizedimg)  # 非gif要用PIL模块的PhotoImage打开
        self.label_img.config(image=photo)
        self.label_img.image = photo  # 显示图片

    def __receive_audio_thread(self, audiosize, slicesize):
        audio_data = []
        for audio_slice in range(audiosize):
            audio_data.append(self.__socket.recv(slicesize))
        player = audioFeatureTest.Play(audio_data)
        root.wait_window(player)

    def __send_av_thread(self, message):
        """
        开启av线程
        :param message: ip地址
        """
        avwindow = openav(message)
        avwindow.start()

    def start(self):
        """
        启动客户端
        """
        self.__socket.connect((ip, 8888))
        root.mainloop()

    def do_login(self, args):
        """
        登录聊天室
        :param args: 参数
        """
        nickname = args.split(' ')[0]

        # 将昵称发送给服务器，获取用户id
        self.__socket.send(
            json.dumps({
                'type': 'login',
                'nickname': nickname
            }).encode())
        # 尝试接受数据
        try:
            buffer = self.__socket.recv(1024).decode()
            obj = json.loads(buffer)
            if obj['id']:
                self.__nickname = nickname
                self.__id = obj['id']
                self.txt_msglist.insert(tkinter.END, '[Client] 成功登录到聊天室\n',
                                        'green')

                # 开启子线程用于接受数据
                thread = threading.Thread(target=self.__receive_message_thread)
                thread.setDaemon(True)
                thread.start()
                self.loginprompt.grid_forget()  # 清除用户名输入部件
                self.button_login.grid_forget()  # 清除登录按钮部件
            else:
                self.txt_msglist.insert(tkinter.END, '[Client] 无法登录到聊天室\n',
                                        'green')
        except Exception:
            self.txt_msglist.insert(tkinter.END, '[Client] 无法从服务器获取数据\n',
                                    'green')

    def do_send(self, args):
        """
        发送消息
        :param args: 参数
        """
        message = args
        # 显示自己发送的消息
        # 注意：str(self.__nickname)后拼接字符串会自动换行，原因不明
        msg = str(self.__nickname) + '(' + str(
            self.__id) + ')' + '[' + time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime()) + ']' + '\n'
        self.txt_msglist.insert(tkinter.END, msg, 'green')  # 添加时间
        self.txt_msglist.insert(tkinter.END, message)  # 获取发送消息，添加文本到消息列表
        # self.txt_msglist.focus_force() #保持光标在最底部，不好
        self.txt_msgsend.delete('0.0', tkinter.END)  # 清空发送消息
        self.txt_msglist.see(tkinter.END)  # 保持显示最底部
        # 开启子线程用于发送数据
        thread = threading.Thread(
            target=self.__send_message_thread, args=(message, ))
        thread.setDaemon(True)
        thread.start()

    def do_send_file(self, args):
        """
        发送文件
        :param args: 此处为文件地址
        """
        filelocation = args
        # 将文件上传至server
        print('[' + str(self.__nickname) + '(' + str(self.__id) + ')' + ']',
              '开始发送文件')
        # 开启子线程用于发送文件
        thread = threading.Thread(
            target=self.__send_file_thread, args=(filelocation, ))
        print('[' + str(self.__nickname) + '(' + str(self.__id) + ')' + ']',
              '发送文件结束')
        thread.setDaemon(True)
        thread.start()

    def do_receive_file(self, fn, fd):
        """
        接收文件
        :param args: 参数
        """
        filename = fn
        filedata = fd
        self.txt_msglist.insert(tkinter.END, '[文件] 开始接收文件\n', 'red')
        # 由于文件较大，因此需要分包传送，根据不同文件的大小，进行大小划分，直到接收数据包的大小等于文件大小为止
        data = b''
        while True:
            part = self.__socket.recv(1024)
            print(len(part))
            data += part
            if len(part) < 1024:
                break
        new_file = open(os.path.join(os.getcwd(), filename),
                        'wb')  # 处理文件名，进行存储
        new_file.write(data)
        new_file.close()
        self.txt_msglist.insert(tkinter.END, '[文件] 文件接收完成\n', 'red')

    def do_receive_img(self, imgname, imgsize):
        """
        接收图片
        :param imgname: 文件名
        :param imgsize: 图片大小
        """
        self.txt_msglist.insert(tkinter.END, '[图片] 图片接收完毕\n', 'red')
        # 开启接收图片，并插入界面的线程
        thread = threading.Thread(target=self.__receive_img_thread, args=(imgname, imgsize, ))
        thread.setDaemon(True)
        thread.start()

    def do_receive_audio(self, audiosize):
        """
        接收音频
        :param audiosize: 音频文件大小
        """
        num = audiosize / 1024.0
        if num != int(num):
            num = int(num) + 1
        else:
            num = int(num)
        new_file = open(os.path.join(os.getcwd(), 'temp_new.wav'),
                        'wb')  # 处理文件名，进行存储
        for i in range(num):
            buffer = self.__socket.recv(1024)
            new_file.write(buffer)

        new_file.close()
        audio_data = 'temp.wav'
        player = audioFeatureTest.Play(audio_data)
        root.wait_window(player)

    def do_send_img(self, args):
        """
        发送图片
        :param args: 图片地址
        """
        imglocation = args
        imgsize = os.path.getsize(imglocation)
        # 判断图片大小，在图片传输中控制图片最大体积
        if imgsize > 204800:
            tkinter.messagebox.showerror('图片过大', '你的图片需要在200KB以下，文件过大可以请使用文件传输')
            return None
        # 将图片发送给server
        print('[' + str(self.__nickname) + '(' + str(self.__id) + ')' + ']',
              '开始发送图片')
        # 开启子线程用于发送图片
        thread = threading.Thread(target=self.__send_img_thread, args=(imglocation, ))
        thread.setDaemon(True)
        thread.start()

    def do_send_audio(self):
        """
        发送语音
        :param args: 语音文件包
        """
        recorder = audioFeatureTest.RecordAudio()
        recorder.run()  # 该数据为音频录音数组
        audio_data = []

        # recorder.close()
        root.wait_window(recorder)
        for i in recorder.getaudio():
            audio_data.append(i)
        # 将声音存储自wav文件传输
        audioFeatureTest.save_wave_file('temp.wav', audio_data)
        print('采集语音完毕')
        thread = threading.Thread(target=self.__send_audio_thread, args=('temp.wav', ))
        thread.setDaemon(True)
        thread.start()

    def avstart(self):
        """
        启动视频客户端：开启广播线程（广播自己ip）+开启av线程（输入对方ip）
        """
        try:
            message = '我已发出视频聊天请求，本人ip地址为：' + str(self.ip)
            # 开启子线程用于广播自己ip
            thread1 = threading.Thread(
                target=self.__send_message_thread, args=(message, ))
            thread1.setDaemon(True)
            thread1.start()
            # 开启子线程用于视频聊天
            thread = threading.Thread(
                target=self.__send_av_thread,
                args=(self.ipprompt.get('0.0', tkinter.END), ))
            self.ipprompt.delete('0.0', tkinter.END)  # 清空发送消息
            thread.setDaemon(True)
            thread.start()
            self.txt_msglist.insert(tkinter.END, '你已发出视频请求，请等待他人连接。\n',
                                    'green')  # 添加时间
        except Exception:
            self.txt_msglist.insert(tkinter.END, '视频连接发生错误，务必先输入目标ip\n',
                                    'green')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='127.0.0.1')
    args = parser.parse_args()
    IP = args.host
    root = tkinter.Tk()
    root.title("网络创新第一队聊天室")
    monitorchat = window(root)
    monitorchat.start()
