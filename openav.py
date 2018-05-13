import sys
import time
from vchat import Video_Server, Video_Client
from achat import Audio_Server, Audio_Client

class openav():
    """选择目标机器开启av"""
    def __init__(self, ip):
        PORT = 11111
        self.vclient = Video_Client(ip, PORT,1, 4)
        self.vserver = Video_Server(PORT-1, 4)
        self.aclient = Audio_Client(ip, PORT+1, 4)
        self.aserver = Audio_Server(PORT+2, 4)

    def start(self):
        self.vclient.start()
        self.aclient.start()
        time.sleep(1)
        self.vserver.start()
        self.aserver.start()
        while True:
            time.sleep(1)
            if not self.vserver.isAlive() or not self.vclient.isAlive():
                print("Video connection lost...")
                sys.exit(0)
            if not self.aserver.isAlive() or not self.aclient.isAlive():
                print("Audio connection lost...")
                sys.exit(0)

