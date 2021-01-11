import socketio
from models import Donation
from datetime import datetime


class LocalClient:
    def __init__(self, database_client):
        sio = socketio.Client()

        @sio.on('event')
        def on_event(event):
            messageId = event['messageId']
            message = event['message'].lower()
            name = event['username']
            message_time = event['messageTime']
            donation = Donation(messageId, name, message)
            database_client.add_donation(donation)

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
    def __init__(self, database_client, token):
        sio = socketio.Client()

        @sio.on('event')
        def on_event(event):
            if(event['type'] == 'donation'):
                messageId = event['event_id'].lower()
                message = event['message'][0]['message']
                name = event['message'][0]['name']
                amount = event['message'][0]['formatted_amount']
                current_time = datetime.now().strftime("%H:%M:%S")
                donation = Donation(messageId, name, message)
                database_client.add_donation(donation)

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
