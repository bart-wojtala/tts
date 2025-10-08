from models import VoiceMessage, GeneratedAudio, Message
import sys
import numpy as np
import requests
import time
from scipy.io.wavfile import write, read
from scipy.signal import lfilter, butter
import soundfile as sf
import pyrubberband as pyrb
from pydub import AudioSegment
from random import randint
from AudioLib import AudioEffect
from tts_engine import TextToSpeechEngine
import nltk



msg = Message('0a', 'bart3s', 'samuel: Do you like what you see? trump let\'s fist is 300 bucks. david: Wow that is cruel')
tts_engine = TextToSpeechEngine('')
generated_audio = tts_engine.generate_audio(msg)