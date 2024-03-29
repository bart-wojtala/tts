import os
import sys
from PyQt5 import Qt
from PyQt5 import QtCore
from PyQt5.QtCore import QMutex, QObject, QRunnable, pyqtSignal, pyqtSlot, QThreadPool
from PyQt5.QtWidgets import QMainWindow
from socket_client import LocalClient, StreamElementsClient, StreamlabsClient
from ui_layout import Ui_MainWindow
import time
import pygame
import traceback
from database_client import DatabaseClient
from tts_engine import TextToSpeechEngine
from configparser import ConfigParser
import qdarkstyle


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

        self.kwargs["progress_callback"] = self.signals.progress
        self.kwargs["elapsed_callback"] = self.signals.elapsed
        self.kwargs["text_ready"] = self.signals.textready

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
    def __init__(self, app, client="", token=""):
        super(GUI, self).__init__()
        self.messages_to_play = []
        self.database_client = DatabaseClient()
        self.local_socket_client = LocalClient(self.database_client)
        self.socket_client = None
        if token:
            if client == 'Streamlabs':
                self.socket_client = StreamlabsClient(
                    self.database_client, token)
            if client == 'StreamElements':
                self.socket_client = StreamElementsClient(
                    self.database_client, token)
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
        self.ClientRemoveAudio.clicked.connect(self.delete_first_message)
        self.ClientRemoveAudio.setEnabled(True)
        self.log_window.ensureCursorVisible()
        self.log_window2.ensureCursorVisible()
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
        print("Multithreading with maximum {} threads".format(
            self.threadpool.maxThreadCount()))
        self.signals = GUISignals()
        self.tts_engine = TextToSpeechEngine(self.generated_audio_path)

    @pyqtSlot(str)
    def draw_text(self, text):
        obj = text[0:4]
        msg = text[5:]
        if obj == "Log1":
            if len(self.logs2) > self.max_log2_lines:
                self.logs2.pop(0)
            self.logs2.append(msg)
            log_text = "\n".join(self.logs2)
            self.log_window.setPlainText(log_text)
            self.log_window.verticalScrollBar().setValue(
                self.log_window.verticalScrollBar().maximum())
        if obj == "Log2":
            self.log_window2.setPlainText(msg)
        if obj == "Sta1":
            self.statusbar.setText(msg)

    @pyqtSlot(int)
    def print_elapsed(self, val):
        pass

    def thread_complete(self):
        pass

    def print_output(self, s):
        pass

    def closeEvent(self, event):
        global _running
        if _running:
            event.ignore()
        else:
            self.local_socket_client.disconnect()
            if self.socket_client:
                self.socket_client.disconnect()
            event.accept()

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
        text_ready.emit("Log1:TTS engine started!")
        while True:
            _mutex1.lock()
            if _running == False:
                _mutex1.unlock()
                break
            else:
                _mutex1.unlock()
            while self.database_client.is_messages_collection_not_empty() and self.connected:
                message = self.database_client.get_first_message_in_queue()
                text_ready.emit("Log2:{} donated!\nID: {}\n{}".format(
                    message.name, message.messageId, message.text))
                try:
                    start_time = time.time()
                    generated_audio = self.tts_engine.generate_audio(message)
                    if generated_audio:
                        text_ready.emit("Sta1:Generating message: {} took: {} seconds.".format(
                            message.messageId, str(round((time.time() - start_time), 2))))
                        generated_audio.messageId = message.messageId
                        self.messages_to_play.append(generated_audio)
                        self.database_client.add_generated_message(message)
                    else:
                        text_ready.emit(
                            "Sta1:Message: {}\nwas automatically skipped!".format(message.messageId))
                    self.database_client.delete_message(message.messageId)
                except:
                    self.connected = False
                    text_ready.emit("Log1:\nCan't connect to TTS server!")
                    self.stop()
                text_ready.emit("Log2:")
            time.sleep(0.5)
        self.ClientStartBtn.setEnabled(True)
        self.ClientStopBtn.setDisabled(True)
        self.ClientSkipAudio.setDisabled(True)
        text_ready.emit("Log1:TTS engine stopped!")
        return "Return value of execute_this_fn"

    def play_audio_fn(self, channel, progress_callback, elapsed_callback, text_ready):
        while True:
            _mutex1.lock()
            if _running == False:
                _mutex1.unlock()
                break
            else:
                _mutex1.unlock()
            while self.messages_to_play:
                if not channel.get_busy() and self.current_audio_length == 0:
                    time.sleep(1)
                    generated_audio = self.messages_to_play.pop(0)
                    name = generated_audio.message.name
                    text = generated_audio.message.text
                    messageId = generated_audio.message.messageId
                    files = generated_audio.files
                    text_ready.emit(
                        "Log1:------------------------------------------------------------------------------------\n")
                    text_ready.emit("Log1:{} donated!".format(name))
                    text_ready.emit("Log1:ID: {}".format(messageId))
                    text_ready.emit("Log1:{}".format(text))
                    self.current_audio_length = generated_audio.length
                    self.files = files
                    while self.current_audio_length > 0:
                        if not channel.get_busy() and len(self.files) > 0:
                            self.playback_wav(self.files.pop(0))

            time.sleep(0.5)
        return "Return value of play_audio_fn"

    def playback_wav(self, file):
        voice = file.voice
        wav = file.text
        if voice == "satan:":
            pygame.mixer.quit()
            pygame.mixer.init(frequency=11000, size=-16, channels=1)
            self.channel = pygame.mixer.Channel(0)
        else:
            pygame.mixer.quit()
            pygame.mixer.init(frequency=22050, size=-16, channels=1)
            self.channel = pygame.mixer.Channel(0)
        sound = pygame.mixer.Sound(wav)
        if voice == "keanu:":
            self.channel.set_volume(self.volumeSlider.value()/100)
        else:
            self.channel.set_volume((self.volumeSlider.value()/100)*0.9)
        self.channel.queue(sound)
        self.current_audio_length -= 1
        self.ClientSkipAudio.setEnabled(True)

    def skip_wav(self):
        if self.channel.get_busy():
            self.files = []
            self.channel.stop()
            self.channel = pygame.mixer.Channel(0)
            self.current_audio_length = 0

    def delete_first_message(self):
        if self.database_client.is_messages_collection_not_empty():
            message = self.database_client.get_first_message_in_queue()
            self.database_client.delete_message(message.messageId)

    def change_volume(self):
        value = self.volumeSlider.value()


if __name__ == "__main__":
    config = ConfigParser()
    config.read("config.ini")
    token = config["StreamElements"]["token"]
    app = Qt.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    window = GUI(app, 'StreamElements', token)
    window.show()
    sys.exit(app.exec_())
