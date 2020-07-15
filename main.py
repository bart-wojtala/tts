import socketio
from models import Donation

class StreamlabsClient:
    def __init__(self, token):
        sio = socketio.Client()
        
        @sio.on('event')
        def on_event(event):
            if(event['type'] == 'donation'):
                donation = Donation(event['message'][0]['name'], event['message'][0]['message'])
                print(donation.name, donation.message)

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
        print('My sid is:', sio.sid)
        sio.wait()

token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6IjE5NTgyN0IxRDJBRDMxREUzQjJBIiwicmVhZF9vbmx5Ijp0cnVlLCJwcmV2ZW50X21hc3RlciI6dHJ1ZSwidHdpdGNoX2lkIjoiMzk2NTk5NTkifQ.jG1vs8NfnS2T5HTcJ_on9-_HokkiO0ACLYevhgUqnfo"
client = StreamlabsClient(token)
