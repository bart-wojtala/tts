from email.mime import audio
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
# from tts_engine import TextToSpeechEngine
import nltk

from sound_utils import write_audio_file


# RESAMPLE AUDIO TO HIGHER QUALITY
# ffmpeg.exe -y -i "%~1" -af "aresample=44100:resampler=soxr:precision=15, equalizer=f=50:width_type=o:width=0.75:g=3.6, equalizer=f=3000:width_type=o:width=1.0:g=2.0, equalizer=f=10000:width_type=o:width=1.0:g=4.0" "%~1_EQ.wav"

# from audio_generator_flowtron import AudioGeneratorFlowtron
# asdas = AudioGeneratorFlowtron()
# audio = asdas.generate('Ziemniaki są pyszne.', 1)
# write_audio_file('.', 'flowtron_test.wav', 'flowtron:', audio, 22050)

from tts_engine_pl import TextToSpeechEnginePL

tts_engine = TextToSpeechEnginePL()
msg = Message('aaaa', 'asd', 'bezi: Do widzenia panie jarku.')
tts_engine.generate_audio(msg)


# from audio_generator_tacotron import AudioGeneratorTacotron
from scipy.io.wavfile import write, read
# asd = "Attention Twitch chat. Did you know that you can use text to speech on this channel? Type exclamation mark test, to play a test message, or use a command exclamation mark tee tee es, to check it yourself!"
asd = "let's talk about me. let's talk about the 6 foot 8 frame the 37 inch verticle leap, the black steel that drips down my back aka the bullet proof mullet. the google prototype scopes with built in LCD LED 1080p 3D sony technology. The Ethiopian poisonous caterpillar aka slick daddy." 
# asd2 = "Let's talk about the cabinets right behind me that go 40 feet deep into the wall that houses the other 95 percent of my trophies, the awards, the certificates, all claiming first place, right? Let me give you a little inside glimpse into the hotshot, video game life style of the two time international video game superstar. Because that's what this channel's about, that's what this domain is about, that's what society is about. You are looking at the new face of Twitch and GODDAMN is Twitch lucky."
# asd = "january february march april may june. July august september october november december."
# asd = "Hello Data Workshop. How are you doing today?"
# asd = "Do you like what you see? Fisting is 300 bucks."
# asd = "Are you fortshn'etly about that un'fortshn'etly quick that."
# asd = "WAKE THE FUCK UP DATA WORKSHOP! We have a model to train."
# asd = "Good evening Bolek. Go fuck yourself."


# asd = "All voices in this veedeo, except mine, were generated yuzing ay eye text to speech tek'nolo'jee. My vyouwers sent chat messages during li'v streams on Twitch, and those messages were converted to audio."
# asd = "That's so sweet, she replies. He doesn't do this very well."
# asd = "What do you think about nigga life matter?"
# asd = "Fuck the polees comin straight from the underground, A young nigga got it bad cause I'm brown. And not the other color so polees think, they have the authority to kill a migh nority!"

# asd = "Do not go gentle into that good night. Old age should burn and rave at close of day. Rage. Rage against the dying of the light."

# vm = VoiceMessage("vader:", asd)
# vm2 = VoiceMessage("gandalf:", asd)
# vm3 = VoiceMessage("trump:", asd)
# vm4 = VoiceMessage("johnny:", asd)
# # vm4 = VoiceMessage("hal:", asd)

# vm = VoiceMessage("geralt:", "Jeśli mam wybierać pomiędzy złem a złem, to jebać kaczyńskiego.")

# file_name = "test_koles.wav"
# # audio_gen = AudioGeneratorTacotron([vm, vm2, vm3, vm4])
# audio_gen = AudioGeneratorTacotron([vm])
# audio, sr = audio_gen.generate()
# write(file_name, sr, audio)


# asd = "Fisting dick_123 DA is $-3.55 #free-21.5642.423.savage glados: trump: Mr. John,Johnson Jr. was born in the U.S.A but earned his Ph.D. in glitchNRG before joining Nike Inc. as an engineer <3. He also worked at :) craigslist.org as a business analyst. samuel: Do you like what you see? Fisting is 300 bucks."
# asd = "trump: hello i am the president of america, funny valentine. i will take the first napkin and make america powerful. dirty deeds done dirt cheap!!! by the way bart the thing i said is from an anime called jojo so you might not understand it"
# asd = 'david: FBI is fbi. fullstop.fullstop.. fullstop.fullstop.. fullstop. fullstop..fullstop.fullstop.. fullstop.fullstop..fullstop.fullstop..fullstop.fullstop.. fullstop.fullstop..fullstop.fullstop.'
# asd = 'a live. should live. I live. to live. going live.'
# asd = "biggie: be el em! be el em! be el em!"
# asd = "johnny: let's talk about me. let's talk about the 6 foot 8 frame the 37 inch verticle leap, the black steel that drips down my back aka the bullet proof mullet. the google prototype scopes with built in LCD LED 1080p 3D sony technology. The Ethiopian poisonous caterpillar aka slick daddy." 


### ---#
# asd = "vader: Do not go gentle into that good night. Old age should burn and rave at close of day. Rage. Rage against the dying of the light."
# donation = Message('asd1', 'fds', asd)

# tts_engine = TextToSpeechEngine()
# donation_audio = tts_engine.generate_audio(donation)

