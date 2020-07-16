import socketio
from models import Donation

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from requests import Session
from threading import Thread
from time import sleep

from tts_engine import TextToSpeechEngine

from pygame import mixer

class StreamlabsClient:
    def __init__(self, token):
        sio = socketio.Client()
        
        @sio.on('event')
        def on_event(event):
            if(event['type'] == 'donation'):
                donation = Donation(event['message'][0]['name'], event['message'][0]['message'])
                new_donations.append(donation)

        @sio.event
        def connect():
            server_messages.append("I'm connected!")

        @sio.event
        def connect_error():
            server_messages.append("The connection failed!")

        @sio.event
        def disconnect():
            server_messages.append("I'm disconnected!")

        sio.connect('https://sockets.streamlabs.com?token=' + token)
        sio.wait()

token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6IjE5NTgyN0IxRDJBRDMxREUzQjJBIiwicmVhZF9vbmx5Ijp0cnVlLCJwcmV2ZW50X21hc3RlciI6dHJ1ZSwidHdpdGNoX2lkIjoiMzk2NTk5NTkifQ.jG1vs8NfnS2T5HTcJ_on9-_HokkiO0ACLYevhgUqnfo"


server = Session()

# GUI:
app = QApplication([])
text_area = QPlainTextEdit()
text_area.setFocusPolicy(Qt.NoFocus)
button = QPushButton("Skip donation")
layout = QVBoxLayout()
layout.addWidget(text_area)
layout.addWidget(button)
window = QWidget()
window.setLayout(layout)
window.show()

# Event handlers:
new_donations = []
server_messages = []
def fetch_new_messages():
    StreamlabsClient(token)

thread = Thread(target=fetch_new_messages, daemon=True)
thread.start()

def display_new_messages():
    generating_audio = False
    while new_donations and not generating_audio:
        generating_audio = True
        donation = new_donations.pop(0)
        text_area.appendPlainText(donation.name + "| " + donation.message)
        tts_engine = TextToSpeechEngine(donation.name, donation.message)
        file_name = tts_engine.generate_audio()
        mixer.init()
        mixer.music.load(file_name)
        mixer.music.set_volume(0.6)
        mixer.music.play()
        generating_audio = False

    while server_messages:
        text_area.appendPlainText("**** " + server_messages.pop(0) + " **")

def on_button_clicked():
    if mixer.music.get_busy():
        text_area.appendPlainText("**** Skipped donation! **")
        mixer.music.stop()
    else:
        text_area.appendPlainText("**** No donation message! **")

button.clicked.connect(on_button_clicked)
timer = QTimer()
timer.timeout.connect(display_new_messages)
timer.start(1000)

app.exec_()
