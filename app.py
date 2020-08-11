from tts_engine import TextToSpeechEngine
from audio_generator import AudioGenerator
from models import VoiceMessage
from flask import Flask, jsonify, request
app = Flask(__name__)


@app.route('/status', methods=['GET'])
def health():
    return "Server OK!"


@app.route('/tts', methods=['GET'])
def convert_message():
    message = request.args.get('message')
    voice = request.args.get('voice')
    log_message(message, voice)
    audio_generator = AudioGenerator([VoiceMessage(voice, message)])
    audio, sampling_rate = audio_generator.generate()
    return jsonify(audio=audio.tolist(), rate=sampling_rate)


@app.route('/singletts', methods=['GET'])
def convert_single_message():
    message = request.args.get('message')
    log_message(message)
    tts_engine = TextToSpeechEngine(message, "", "", None)
    audio, sampling_rate = tts_engine.generate_single_audio()
    return jsonify(audio=audio.tolist(), rate=sampling_rate)


def log_message(message, voice=''):
    if voice:
        print("[LOG] Requested message: ", voice, message)
    else:
        print("[LOG] Requested message: ", message)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9000)
