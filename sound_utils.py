import time
from scipy.io.wavfile import write
from scipy.signal import butter, lfilter
import soundfile as sf
import pyrubberband as pyrb
from pydub import AudioSegment
from random import randint
from AudioLib import AudioEffect


def write_audio_file(path, name, voice, audio, sampling_rate):
    file_name = path + \
        time.strftime("%Y%m%d-%H%M%S_") + name + str(randint(0, 100)) + ".wav"
    if voice == "satan:":
        temp_file_name = path + "temp.wav"
        write(temp_file_name, sampling_rate, audio)

        fixed_framerate = 11000
        sound = AudioSegment.from_file(temp_file_name)
        sound = sound.set_frame_rate(fixed_framerate)
        write(file_name, fixed_framerate, audio)

        y, sr = sf.read(file_name)
        y_stretch = pyrb.time_stretch(y, sr, 1.6)
        y_shift = pyrb.pitch_shift(y, sr, 1.6)
        sf.write(file_name, y_stretch, sr, format='wav')

        sound = AudioSegment.from_wav(file_name)
        sound.export(file_name, format="wav")
    elif voice == "vader:":
        temp_file_name = path + "temp.wav"
        write(temp_file_name, sampling_rate, audio)
        AudioEffect.robotic(temp_file_name, file_name)

        y, sr = sf.read(file_name)
        y_stretch = pyrb.time_stretch(y, sr, 0.9)
        y_shift = pyrb.pitch_shift(y, sr, 0.9)
        sf.write(file_name, y_stretch, sr, format='wav')

        sound = AudioSegment.from_wav(file_name)
        sound.export(file_name, format="wav")
    else:
        write(file_name, sampling_rate, audio)
    return file_name


def butter_params(low_freq, high_freq, fs, order=5):
    nyq = 0.5 * fs
    low = low_freq / nyq
    high = high_freq / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, low_freq, high_freq, fs, order=5):
    b, a = butter_params(low_freq, high_freq, fs, order=order)
    y = lfilter(b, a, data)
    return y
