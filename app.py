from tts_engine import TextToSpeechEngine
from flask import Flask, jsonify, request
app = Flask(__name__)


@app.route('/status', methods=['GET'])
def health():
    return "Server OK!"

@app.route('/tts', methods=['GET'])
def convert_message():
    message = request.args.get('message')
    print(message)
    tts_engine = TextToSpeechEngine(message)
    audio, sampling_rate = tts_engine.generate_audio()
    return jsonify(audio=audio.tolist(), rate=sampling_rate)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
