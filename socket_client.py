import socketio
from models import Donation
from datetime import datetime


class LocalClient:
    def __init__(self, database_client):
        self.sio = socketio.Client()

        @self.sio.on('event')
        def on_event(event):
            messageId = event['messageId']
            message = event['message'].lower()
            name = event['username']
            message_time = event['messageTime']
            donation = Donation(messageId, name, message)
            database_client.add_donation(donation)

        @self.sio.event
        def connect():
            print("I'm connected!")

        @self.sio.event
        def connect_error():
            print("The connection failed!")

        @self.sio.event
        def disconnect():
            print("I'm disconnected!")

        self.sio.connect('http://localhost:3000')

    def disconnect(self):
        self.sio.disconnect()


class StreamlabsClient:
    def __init__(self, database_client, token):
        self.sio = socketio.Client()

        @self.sio.on('event')
        def on_event(event):
            if(event['type'] == 'donation'):
                messageId = event['event_id'].lower()
                message = event['message'][0]['message']
                name = event['message'][0]['name']
                amount = event['message'][0]['formatted_amount']
                current_time = datetime.now().strftime("%H:%M:%S")
                donation = Donation(messageId, name, message)
                database_client.add_donation(donation)

        @self.sio.event
        def connect():
            print("I'm connected!")

        @self.sio.event
        def connect_error():
            print("The connection failed!")

        @self.sio.event
        def disconnect():
            print("I'm disconnected!")

        self.sio.connect('https://sockets.streamlabs.com?token=' + token)

    def disconnect(self):
        self.sio.disconnect()
