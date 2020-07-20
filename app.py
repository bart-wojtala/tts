from tts_engine import TextToSpeechEngine
from flask import Flask, jsonify
app = Flask(__name__)


@app.route('/')
def health():
    return "Server OK!"

@app.route('/<message>')
def convert_message(message):
    tts_engine = TextToSpeechEngine(message)
    audio, sampling_rate = tts_engine.generate_audio()
    return jsonify(audio=audio.tolist(), rate=sampling_rate)

if __name__ == '__main__':
    app.run()
