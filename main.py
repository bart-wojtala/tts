import socketio

class StreamlabsClient:
    def __init__(self, token):
        sio = socketio.Client()
        
        @sio.on('event')
        def on_event(event):
            print(event)
            print('I received an event!')

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
        print('my sid is', sio.sid)
        sio.wait()

token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6IjE5NTgyN0IxRDJBRDMxREUzQjJBIiwicmVhZF9vbmx5Ijp0cnVlLCJwcmV2ZW50X21hc3RlciI6dHJ1ZSwidHdpdGNoX2lkIjoiMzk2NTk5NTkifQ.jG1vs8NfnS2T5HTcJ_on9-_HokkiO0ACLYevhgUqnfo"
client = StreamlabsClient(token)
