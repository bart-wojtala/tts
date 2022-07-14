import socketio
from models import Message
from datetime import datetime
import hashlib


class LocalClient:
    def __init__(self, database_client):
        self.sio = socketio.Client()

        @self.sio.on('event')
        def on_event(event):
            messageId = event['messageId']
            text = event['message'].lower()
            name = event['username']
            message = Message(messageId, name, text)
            database_client.add_message(message)

        @self.sio.event
        def connect():
            print("I'm connected to local socket server!")

        @self.sio.event
        def connect_error():
            print("The connection to local socket server failed!")

        @self.sio.event
        def disconnect():
            print("I'm disconnected from local socket server!")

        self.sio.connect('http://localhost:3000')

    def disconnect(self):
        self.sio.disconnect()


class StreamlabsClient:
    def __init__(self, database_client, token):
        self.sio = socketio.Client()

        @self.sio.on('event')
        def on_event(event):
            event_type = event['type']
            if event_type == 'donation' or event_type == 'subscription' or event_type == 'resub':
                messageId = event['event_id'].lower()
                text = event['message'][0]['message']
                name = event['message'][0]['name']
                message = Message(messageId, name, text, event_type)
                database_client.add_message(message)
            elif event_type == 'bits':
                messageId = event['event_id'].lower()
                text = event['message'][0]['message'].split(' ', 1)[1]
                name = event['message'][0]['name']
                message = Message(messageId, name, text, event_type)
                database_client.add_message(message)

        @self.sio.event
        def connect():
            print("I'm connected to Streamlabs socket API!")

        @self.sio.event
        def connect_error():
            print("The connection to Streamlabs socket API failed!")

        @self.sio.event
        def disconnect():
            print("I'm disconnected from Streamlabs socket API!")

        self.sio.connect(
            'https://sockets.streamlabs.com?token={}'.format(token))

    def disconnect(self):
        self.sio.disconnect()


class StreamElementsClient:
    def __init__(self, database_client, token):
        self.sio = socketio.Client()

        @self.sio.on('event')
        def on_event(event, data):
            listener = event['listener']
            if listener == 'subscriber-latest':
                current_event = event['event']
                event_type = current_event['type']
                messageId = hashlib.md5(
                    str(datetime.now().timestamp()).encode('utf-8')).hexdigest()
                text = current_event['message']
                name = current_event['name']
                message = Message(messageId, name, text, event_type)
                database_client.add_message(message)
            elif listener == 'tip-latest':
                current_event = event['event']
                event_type = current_event['type']
                messageId = hashlib.md5(
                    str(datetime.now().timestamp()).encode('utf-8')).hexdigest()
                text = current_event['message']
                name = current_event['name']
                message = Message(messageId, name, text, event_type)
                database_client.add_message(message)
            elif listener == 'cheer-latest':
                current_event = event['event']
                event_type = current_event['type']
                messageId = hashlib.md5(
                    str(datetime.now().timestamp()).encode('utf-8')).hexdigest()
                text = current_event['message']
                name = current_event['name']
                message = Message(messageId, name, text, event_type)
                database_client.add_message(message)

        @self.sio.on('event:test')
        def on_event_test(event, data):
            listener = event['listener']
            if listener == 'subscriber-latest':
                current_event = event['event']
                event_type = current_event['type']
                messageId = hashlib.md5(
                    str(datetime.now().timestamp()).encode('utf-8')).hexdigest()
                text = current_event['message']
                name = current_event['name']
                message = Message(messageId, name, text, event_type)
                database_client.add_message(message)
            elif listener == 'tip-latest':
                current_event = event['event']
                event_type = current_event['type']
                messageId = hashlib.md5(
                    str(datetime.now().timestamp()).encode('utf-8')).hexdigest()
                text = current_event['message']
                name = current_event['name']
                message = Message(messageId, name, text, event_type)
                database_client.add_message(message)
            elif listener == 'cheer-latest':
                current_event = event['event']
                event_type = current_event['type']
                messageId = hashlib.md5(
                    str(datetime.now().timestamp()).encode('utf-8')).hexdigest()
                text = current_event['message']
                name = current_event['name']
                message = Message(messageId, name, text, event_type)
                database_client.add_message(message)

        @self.sio.event
        def connect():
            self.sio.emit('authenticate', {
                          'method': 'jwt', 'token': token, 'transports': ['websocket', 'polling']})
            print("I'm connected to StreamElements socket API!")

        @self.sio.event
        def connect_error(error):
            print("The connection to StreamElements socket API failed!")
            print(error)

        @self.sio.event
        def disconnect():
            print("I'm disconnected from StreamElements socket API!")

        self.sio.connect(
            'https://realtime.streamelements.com', transports=['websocket'])

    def disconnect(self):
        self.sio.disconnect()
