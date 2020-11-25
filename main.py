import socketio
import os
import sys
from PyQt5 import Qt
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QMutex, QObject, QRunnable, pyqtSignal, pyqtSlot, QThreadPool, QTimer
from PyQt5.QtWidgets import QWidget, QMainWindow, QHeaderView, QMessageBox, QFileDialog
from ui_layout import Ui_MainWindow
import time
import pygame
import traceback
from scipy.io.wavfile import write
from models import Donation, DonationAudio
from tts_engine import TextToSpeechEngine
import requests
import numpy as np
from configparser import ConfigParser
from datetime import datetime


class LocalClient:
    def __init__(self, donations_list):
        sio = socketio.Client()

        @sio.on('event')
        def on_event(event):
            message = event['message']
            name = event['username']
            message_time = event['messageTime']
            print("\n--- " + message_time + "| " +
                  name + " sent a message: " + message)
            donation = Donation(name, message)
            donations_list.append(donation)

        @sio.event
        def connect():
            print("I'm connected!")

        @sio.event
        def connect_error():
            print("The connection failed!")

        @sio.event
        def disconnect():
            print("I'm disconnected!")

        sio.connect('http://localhost:3000')


class StreamlabsClient:
    def __init__(self, donations_list, token):
        sio = socketio.Client()

        @sio.on('event')
        def on_event(event):
            if(event['type'] == 'donation'):
                message = event['message'][0]['message']
                name = event['message'][0]['name']
                amount = event['message'][0]['formatted_amount']
                current_time = datetime.now().strftime("%H:%M:%S")
                print("\n--- " + current_time + "| " + name +
                      " donated " + amount + ": " + message)
                donation = Donation(name, message)
                donations_list.append(donation)

        @sio.event
        def connect():
            print("I'm connected!")

        @sio.event
        def connect_error():
            print("The connection failed!")

        @sio.event
        def disconnect():
            print("I'm disconnected!")

        sio.connect('https://sockets.streamlabs.com?token=' + token)


_mutex1 = QMutex()
_running = False


class WorkerSignals(QObject):
    textready = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    elapsed = pyqtSignal(int)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.kwargs['progress_callback'] = self.signals.progress
        self.kwargs['elapsed_callback'] = self.signals.elapsed
        self.kwargs['text_ready'] = self.signals.textready

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class GUISignals(QObject):
    progress = pyqtSignal(int)
    elapsed = pyqtSignal(int)


class GUI(QMainWindow, Ui_MainWindow):
    def __init__(self, app, instance_url, streamlabs_token=''):
        super(GUI, self).__init__()
        self.donation_list = []
        self.donations_to_play = []
        if streamlabs_token:
            StreamlabsClient(self.donation_list, streamlabs_token)
        else:
            LocalClient(self.donation_list)
        self.url = "http://" + instance_url + ":9000"
        self.app = app
        self.setupUi(self)
        self.setWindowTitle("bart3s tts")
        self.setFixedWidth(600)
        self.setFixedHeight(600)

        self.logs = []
        self.logs2 = []
        self.max_log_lines = 100
        self.max_log2_lines = 100
        self.connected = False
        self.current_audio_length = 0
        self.files = []

        self.ClientSkipAudio.clicked.connect(self.skip_wav)
        self.ClientStopBtn.setDisabled(True)
        self.ClientSkipAudio.setDisabled(True)
        self.log_window.ensureCursorVisible()
        self.volumeSlider.valueChanged.connect(self.change_volume)

        pygame.mixer.quit()
        pygame.mixer.init(frequency=22050, size=-16, channels=1)
        self.channel = pygame.mixer.Channel(0)

        self.generated_audio_path = "generated_audio/"
        if not os.path.exists(self.generated_audio_path):
            os.makedirs(self.generated_audio_path)

        self.ClientStartBtn.clicked.connect(self.start)
        self.ClientStopBtn.clicked.connect(self.stop)
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(3)
        print("Multithreading with maximum %d threads" %
              self.threadpool.maxThreadCount())
        self.signals = GUISignals()

    @pyqtSlot(str)
    def draw_text(self, text):
        obj = text[0:4]
        msg = text[5:]
        if obj == 'Log1':
            if len(self.logs2) > self.max_log2_lines:
                self.logs2.pop(0)
            self.logs2.append(msg)
            log_text = '\n'.join(self.logs2)
            self.log_window.setPlainText(log_text)
            self.log_window.verticalScrollBar().setValue(
                self.log_window.verticalScrollBar().maximum())
        if obj == 'Sta1':
            self.statusbar.setText(msg)

    @pyqtSlot(int)
    def print_elapsed(self, val):
        pass

    def thread_complete(self):
        pass

    def print_output(self, s):
        pass

    def start(self):
        global _running
        _mutex1.lock()
        _running = True
        _mutex1.unlock()
        self.connected = True
        worker = Worker(self.execute_this_fn, self.channel)
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.textready.connect(self.draw_text)

        self.threadpool.start(worker)

        worker2 = Worker(self.play_audio_fn, self.channel)
        worker2.signals.result.connect(self.print_output)
        worker2.signals.finished.connect(self.thread_complete)
        worker2.signals.textready.connect(self.draw_text)

        self.threadpool.start(worker2)

    def stop(self):
        global _running
        _mutex1.lock()
        _running = False
        _mutex1.unlock()
        self.skip_wav()

    def execute_this_fn(self, channel, progress_callback, elapsed_callback, text_ready):
        self.ClientStartBtn.setDisabled(True)
        self.ClientStopBtn.setEnabled(True)
        self.ClientSkipAudio.setEnabled(True)
        text_ready.emit('Log1:Initializing')
        while True:
            _mutex1.lock()
            if _running == False:
                _mutex1.unlock()
                break
            else:
                _mutex1.unlock()
            text_ready.emit("Sta1:Waiting for incoming donations...")
            while self.donation_list and self.connected:
                donation = self.donation_list.pop(0)
                print("\n--- Handling message from " +
                      donation.name + " | " + donation.message)
                try:
                    start_time = time.time()
                    tts_engine = TextToSpeechEngine(
                        donation, donation.name, self.url, self.generated_audio_path)
                    donation_audio = tts_engine.generate_audio()
                    print("\n--- Generating audio took %s seconds" %
                          round((time.time() - start_time), 2))
                    self.donations_to_play.append(donation_audio)
                except:
                    self.connected = False
                    text_ready.emit(
                        "Log1:\n## Can't connect to TTS server! ##")
                    self.stop()
                    self.donation_list.insert(0, donation)
            time.sleep(0.5)
        self.ClientStartBtn.setEnabled(True)
        self.ClientStopBtn.setDisabled(True)
        self.ClientSkipAudio.setDisabled(True)
        text_ready.emit('Log1:\nDisconnected')
        return 'Return value of execute_this_fn'

    def play_audio_fn(self, channel, progress_callback, elapsed_callback, text_ready):
        while True:
            _mutex1.lock()
            if _running == False:
                _mutex1.unlock()
                break
            else:
                _mutex1.unlock()
            while self.donations_to_play:
                if not channel.get_busy() and self.current_audio_length == 0:
                    time.sleep(2)
                    donation_audio = self.donations_to_play.pop(0)
                    name = donation_audio.donation.name
                    msg = donation_audio.donation.message
                    files = donation_audio.files
                    text_ready.emit("Log1:\n###########################\n")
                    text_ready.emit("Log1:" + name + ' donated message:')
                    text_ready.emit("Log1:" + msg)
                    text_ready.emit(
                        'Sta1:Currently playing -> ' + name + ' | ' + msg)
                    self.current_audio_length = donation_audio.length
                    self.files = files
                    while self.current_audio_length > 0:
                        if not channel.get_busy() and len(self.files) > 0:
                            self.playback_wav(self.files.pop(0))

            time.sleep(0.5)
        return 'Return value of play_audio_fn'

    def playback_wav(self, file):
        voice = file.voice
        wav = file.message
        if voice == "satan:":
            pygame.mixer.quit()
            pygame.mixer.init(frequency=11000, size=-16, channels=1)
            self.channel = pygame.mixer.Channel(0)
        else:
            pygame.mixer.quit()
            pygame.mixer.init(frequency=22050, size=-16, channels=1)
            self.channel = pygame.mixer.Channel(0)
        sound = pygame.mixer.Sound(wav)
        self.channel.queue(sound)
        self.current_audio_length -= 1
        self.ClientSkipAudio.setEnabled(True)

    def skip_wav(self):
        if self.channel.get_busy():
            self.files = []
            self.channel.stop()
            self.channel = pygame.mixer.Channel(0)
            self.current_audio_length = 0

    def change_volume(self):
        value = self.volumeSlider.value()
        self.channel.set_volume(value/100)


if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')
    url = config['GCP']['url']
    # token = config['Streamlabs']['token']
    app = Qt.QApplication(sys.argv)
    window = GUI(app, url)
    window.show()
    sys.exit(app.exec_())
