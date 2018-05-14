# -*- coding: utf-8 -*-
import socket
import threading
import json


class Server:
    """
    服务器类，用来接收并处理消息
    """
    def __init__(self):
        """
        构造
        """
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 初始化socket
        self.__connections = list()  # 所有用户的连接列表
        self.__nicknames = list()  # 所有用户的用户名
        self.host = socket.gethostname()  # 获取主机的名称，并通过下面的语句获取ip
        self.ip = socket.gethostbyname(socket.gethostname())

    def __user_thread(self, user_id):
        """
        用户子线程
        :param user_id: 用户id
        """
        connection = self.__connections[user_id]
        nickname = self.__nicknames[user_id]
        print('[Server] 用户', user_id, nickname, '加入聊天室')
        self.__broadcast(message='用户 ' + str(nickname) + '(' + str(user_id) + ')' + '加入聊天室\n')

        # 侦听
        while True:
            # noinspection PyBroadException
            try:
                buffer = connection.recv(1024).decode()
                # 解析成json数据
                if buffer:
                    obj = json.loads(buffer)
                    # 如果是广播指令
                    if obj['type'] == 'broadcast':
                        self.__broadcast(obj['sender_id'], obj['message'])
                    # 如果是文件，则进入广播文件函数
                    elif obj['type'] == 'file':
                        print('[Server] 开始广播文件')
                        self.__broadfile(user_id=obj['sender_id'], message=obj['message'], filename=obj['filename'], connection=connection)
                    # 如果收到图片，则进入广播图片函数
                    elif obj['type'] == 'img':
                        print('[Server] 开始广播图片')
                        self.__broadfile(user_id=obj['sender_id'], message=obj['message'], filename=obj['imgname'], connection=connection, filetype='img')
                    # 如果收到音频，则广播音频
                    elif obj['type'] == 'audio':
                        print('[Server] 开始广播音频')
                        self.__broadaudio(user_id=obj['sender_id'], message=obj['message'], connection=connection)
                    else:
                        print('[Server] 无法解析json数据包:', connection.getsockname(), connection.fileno())
            except Exception as e:
                print('[Server] 连接失效:', connection.getsockname(), connection.fileno())
                print(e)
        self.__connections[user_id].close()
        self.__connections[user_id] = None
        self.__nicknames[user_id] = None

    def __broadcast(self, user_id=0, message=''):
        """
        广播
        :param user_id: 用户id(0为系统)
        :param message: 广播内容
        """
        for i in range(1, len(self.__connections)):
            if user_id != i:
                self.__connections[i].send(json.dumps({
                    'sender_id': user_id,
                    'sender_nickname': self.__nicknames[user_id],
                    'message': message,
                    'type': 'text'
                }).encode())

    def __broadfile(self, connection, user_id=0, message='', filename='', filetype='file'):
        """
        广播文件包
        :param connection: 发文件用户的连接，用来接收数据
        :param user_id: 用户id(0为系统)
        :param message: 文件大小
        :param filename: 文件名
        """
        for i in range(1, len(self.__connections)):
            if user_id != i:
                self.__connections[i].send(json.dumps({
                    'sender_id': user_id,
                    'sender_nickname': self.__nicknames[user_id],
                    'message': message,
                    'type': filetype,
                    'filename': filename
                }).encode())
        # 为每一个用户广播数据包，进行数据传输
        while True:
            part = connection.recv(1024)
            print(len(part))
            for i in range(1, len(self.__connections)):
                if user_id != i:
                    self.__connections[i].send(part)
            if len(part) < 1024:
                break
        if filetype == 'file':
            print('文件广播结束')
        elif filetype == 'img':
            print('图片广播结束')

    def __broadaudio(self, connection, user_id=0, message=0):
        """
        :param connection: 发文件用户的连接，用来接收数据
        :param user_id: 用户id(0为系统)
        :param message: 语音文件大小
        """
        for i in range(1, len(self.__connections)):
            if user_id != i:
                self.__connections[i].send(json.dumps({
                    'sender_id': user_id,
                    'sender_nickname': self.__nicknames[user_id],
                    'message': message,
                    'type': 'audio'
                }).encode())
        # 为每一个用户广播数据包，进行数据传输
        num = message/1024.0  # 计算存储转发的次数
        if num != int(num):
            num = int(num)+1
        else:
            num = int(num)
        for i in range(num):
            buffer = connection.recv(1024)  # 这里以1024为一个数据包进行存储并转发给其他所有用户
            for j in range(1, len(self.__connections)):
                if user_id != j:
                    self.__connections[j].send(buffer)
        print('广播音频结束')

    def start(self):
        """
        启动服务器
        """
        # 绑定端口
        self.__socket.bind((self.ip, 8888))
        # 启用监听
        self.__socket.listen(10)
        print('[Server] 服务器正在运行......')

        # 清空连接
        self.__connections.clear()
        self.__nicknames.clear()
        self.__connections.append(None)
        self.__nicknames.append('System')

        # 开始侦听
        while True:
            connection, address = self.__socket.accept()  # 解析收到的连接和地址
            print('[Server] 收到一个新连接', connection.getsockname(), connection.fileno())

            # 尝试接受数据
            try:
                buffer = connection.recv(1024).decode()
                # 解析成json数据
                obj = json.loads(buffer)
                # 如果是连接指令，那么则返回一个新的用户编号，接收用户连接
                if obj['type'] == 'login':
                    self.__connections.append(connection)
                    self.__nicknames.append(obj['nickname'])
                    connection.send(json.dumps({
                        'id': len(self.__connections) - 1
                    }).encode())

                    # 开辟一个新的线程用于监听处理该用户的所有消息
                    thread = threading.Thread(target=self.__user_thread, args=(len(self.__connections) - 1, ))
                    thread.setDaemon(True)  # 设置线程为守护线程，交给python程序管理
                    thread.start()
                else:
                    print('[Server] 无法解析json数据包:', connection.getsockname(), connection.fileno())
            except Exception:
                print('[Server] 无法接受数据:', connection.getsockname(), connection.fileno())


server = Server()
server.start()
