import pyaudio
import wave
import tkinter as tk
import tkinter.messagebox
import threading

audio_buffer = []

NUM_SAMPLES = 1024
FRAMERATE = 44100
FORMAT = pyaudio.paInt16
SAMPYWIDTH = 2
CHANNELS = 2
MAXTIME = 5


class RecordAudio(tk.Toplevel):
    """
    从客户端获取声音
    """
    def __init__(self):
        super().__init__()
        # 屏幕居中现实
        self['width'] = 200
        self['height'] = 50
        self.update()
        curWidth = int(self.winfo_reqwidth())
        curHeight = int(self.winfo_height())
        scnWidth, scnHeight = self.maxsize()  # 获取现有root的大小
        # 产生窗口所需改变参数
        tmpcnf = '%dx%d+%d+%d' % (curWidth, curHeight,
                                  (scnWidth - curWidth) / 2,
                                  (scnHeight - curHeight) / 2)
        self.geometry(tmpcnf)
        self.NUM_SAMPLES = NUM_SAMPLES
        self.framerate = FRAMERATE
        self.format = FORMAT
        self.channels = CHANNELS
        self.flag = True
        self.time = MAXTIME

    def my_button(self, root, label_text, button1_text, button1_func,
                  button2_text, button2_func):
        """
        制作用来录音的button按钮和面板
        """
        self.label = tk.Label(root)
        self.label['text'] = label_text
        self.label.pack()
        self.button1 = tk.Button(root)
        self.button1['text'] = button1_text
        self.button1['command'] = button1_func
        self.button2 = tk.Button(root)
        self.button2['text'] = button2_text
        self.button2['command'] = button2_func
        self.button1.pack()
        # self.button2.pack()

    def do_record_wave(self):
        self.button1.pack_forget()
        self.button2.pack()
        thread = threading.Thread(target=self.record_wave)
        thread.setDaemon(True)
        thread.start()

    def record_wave(self):
        """
        录制声音
        """
        # self.button1.pack_forget()
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=self.format,
            channels=self.channels,
            rate=self.framerate,
            input=True,
            frames_per_buffer=self.NUM_SAMPLES)
        count = 0
        while self.flag and count < int(
                self.framerate / self.NUM_SAMPLES * self.time):
            frame_data = stream.read(self.NUM_SAMPLES)
            audio_buffer.append(frame_data)
            count += 1
            # print('.')
        else:
            tkinter.messagebox.showinfo('录音结束', '完成录音')
            self.destroy()

    def stop_wave(self):
        self.flag = False

    def run(self):
        self.my_button(self, '录音,您最长可以录5秒钟', '开始录音', self.do_record_wave, '停止录音',
                       self.stop_wave)

    def getaudio(self):
        return audio_buffer


class Play(tk.Toplevel):
    """
    播放声音类
    """
    def __init__(self, audio_data):
        super().__init__()
        self['width'] = 200
        self['height'] = 50
        self.update()
        curWidth = int(self.winfo_reqwidth())
        curHeight = int(self.winfo_height())
        scnWidth, scnHeight = self.maxsize()  # 获取现有root的大小
        # 产生窗口所需改变参数
        tmpcnf = '%dx%d+%d+%d' % (curWidth, curHeight,
                                  (scnWidth - curWidth) / 2,
                                  (scnHeight - curHeight) / 2)
        self.geometry(tmpcnf)
        label = tk.Label(self, text='您可以反复听哦')
        label.pack()
        button = tk.Button(self, text='点击收听', command=lambda: self.do_play(audio_data, ))
        button.pack()

    def do_play(self, audio_data):
        thread = threading.Thread(target=self.play, args=(audio_data,))
        thread.setDaemon(True)
        thread.start()

    def play(self, audio_data):
        p = pyaudio.PyAudio()
        wf = wave.open(audio_data, 'rb')
        data = wf.readframes(NUM_SAMPLES)
        stream = p.open(
            format=FORMAT, channels=CHANNELS, rate=FRAMERATE, frames_per_buffer=NUM_SAMPLES, output=True)
        # for voice in audio_data:
        #     stream.write(voice)
        while data != '':
            stream.write(data)
            data = wf.readframes(NUM_SAMPLES)
        stream.stop_stream()
        stream.close()
        wf.close()


def save_wave_file(filename, data):
    '''''save the date to the wav file'''
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(SAMPYWIDTH)
    wf.setframerate(FRAMERATE)
    wf.writeframes(b"".join(data))
    wf.close()


if __name__ == '__main__':
    # root = tk.Tk()
    # root.update()
    # curWidth = root.winfo_screenmmwidth
    # curHeight = root.winfo_screenheight
    # scnWidth, scnHeight = root.maxsize()  # get screen width and height
    # # now generate configuration information
    # tmpcnf = '%dx%d+%d+%d' % (curWidth, curHeight, (scnWidth - curWidth) / 2,
    #                           (scnHeight - curHeight) / 2)
    # root.geometry(tmpcnf)
    r = RecordAudio()
    r.run()
