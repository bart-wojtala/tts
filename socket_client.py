import socketio
from models import Message
from datetime import datetime


class LocalClient:
    def __init__(self, database_client):
        self.sio = socketio.Client()

        @self.sio.on('event')
        def on_event(event):
            messageId = event['messageId']
            message = event['message'].lower()
            name = event['username']
            message = Message(messageId, name, message)
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
                message = event['message'][0]['message']
                name = event['message'][0]['name']
                message = Message(messageId, name, message, event_type)
                database_client.add_message(message)
            elif event_type == 'bits':
                messageId = event['event_id'].lower()
                message = event['message'][0]['message'].split(' ', 1)[1]
                name = event['message'][0]['name']
                message = Message(messageId, name, message, event_type)
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

        self.sio.connect('https://sockets.streamlabs.com?token=' + token)

    def disconnect(self):
        self.sio.disconnect()
