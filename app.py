from flask import Flask
app = Flask(__name__)


@app.route('/')
def health():
    return "Server OK!"

@app.route('/<message>')
def convert_message(message):
    return message

if __name__ == '__main__':
    app.run()
