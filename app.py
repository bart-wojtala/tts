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
    print(voice + ' ' + message)
    # tts_engine = TextToSpeechEngine(message)
    # audio, sampling_rate = tts_engine.generate_audio()
    message_list = []
    message_list.append(VoiceMessage(voice, message))
    audio_generator = AudioGenerator(message_list)
    audio, sampling_rate = audio_generator.generate()
    return jsonify(audio=audio.tolist(), rate=sampling_rate)

@app.route('/singletts', methods=['GET'])
def convert_single_message():
    message = request.args.get('message')
    print(message)
    tts_engine = TextToSpeechEngine(message, None, None)
    audio, sampling_rate = tts_engine.generate_single_audio()
    return jsonify(audio=audio.tolist(), rate=sampling_rate)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9000)
