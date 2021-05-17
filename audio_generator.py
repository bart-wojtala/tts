import os
import platform
import time
import sys
sys.path.append("tacotron2/")
sys.path.append("tacotron2/waveglow/")
from scipy.io.wavfile import read
import pyttsx3
from denoiser import Denoiser
from text import text_to_sequence
from hparams import create_hparams
import numpy as np
import torch
from train import load_model


class AudioGenerator:
    models_22khz = {
        "carlson:": "tuck2",
        "daria:": "daria22_model",
        "david:": "attenborough_checkpoint_824800",
        "duke:": "duke_53795",
        "gandalf:": "gandalf_checkpoint_23932",
        "glados:": "glados_7325",
        "hal:": "hal_9000",
        "hudson:": "hudson-horstachio-22khz",
        "johnny:": "johnny_353780",
        "keanu:": "keanu_67912",
        "mlpab:": "Apple_Bloom_28037_0.120",
        "mlpaj:": "Applejack_40071_0.156",
        "mlpca:": "Celestia_38429_0.167",
        "mlpfy:": "Fluttershy_46598_0.101",
        "mlppp:": "Pinkie_Pie_46853_0.119",
        "mlprd:": "Rainbow_Dash_62638_0.228",
        "mlpts:": "Twilight_Sparkle_42660_0.179",
        "mlpza:": "Zecora_8977_0.058",
        "neil:": "neil_tyson_checkpoint_500000",
        "samuel:": "slj_117480",
        "satan:": "tacotron2_statedict.pt",
        "trevor:": "trevor_18180",
        "trump:": "trump_7752",
        "vader:": "jej_checkpoint_904500",
        "woman:": "tacotron2_statedict.pt"
    }

    synth_voices_linux = {
        "stephen:": "default"
    }

    synth_voices_windows = {
        "msdavid:": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_DAVID_11.0",
        "stephen:": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\eSpeakNG_en"
    }

    waveglow_22khz = {
        "david:": "attenborough_waveglow_1516200",
        "default": "waveglow_256channels.pt",
        "johnny:": "waveglow_johnny_516600.pt",
        "samuel:": "waveglow_slj_227400.pt",
        "vader:": "jej_waveglow_890k"
    }

    def __init__(self, messages):
        self.messages = messages
        self.joined_audio = np.empty(1,)
        self.silence = np.zeros(11000,)
        self.current_os = platform.system()
        self.audio_length_parameter = 32767
        self.default_sampling_rate = 22050
        self.models_path = "models/"
        self.hparams = create_hparams()
        self.hparams.sampling_rate = self.default_sampling_rate
        self.temp_file = "temp.wav"

    def generate(self):
        for message in self.messages:
            if message.voice in self.models_22khz:
                self.hparams.sampling_rate = self.default_sampling_rate
                waveglow_path = ""
                if message.voice == "vader:" or message.voice == "duke:":
                    waveglow_path = self.models_path + \
                        self.waveglow_22khz["vader:"]
                elif message.voice == "keanu:" or message.voice == "hal:":
                    waveglow_path = self.models_path + \
                        self.waveglow_22khz["david:"]
                elif message.voice == "johnny:":
                    waveglow_path = self.models_path + \
                        self.waveglow_22khz["johnny:"]
                else:
                    waveglow_path = self.models_path + \
                        self.waveglow_22khz["default"]

                waveglow = torch.load(waveglow_path)["model"]
                waveglow.cuda().eval().half()
                for k in waveglow.convinv:
                    k.float()
                denoiser = Denoiser(waveglow)

                if len(message.text) > 127:
                    self.hparams.max_decoder_steps = 100000
                else:
                    self.hparams.max_decoder_steps = 10000

                trimmed_message_length = len(
                    "".join(c for c in message.text if c.isalnum()))
                if trimmed_message_length < 4:
                    if message.voice == "vader:" or message.voice == "carlson:":
                        self.hparams.max_decoder_steps = 1000
                        self.hparams.gate_threshold = 0.001
                        if any(char.isdigit() for char in message.text):
                            self.hparams.max_decoder_steps = 10000
                            self.hparams.gate_threshold = 0.5
                if trimmed_message_length >= 4 and trimmed_message_length < 7:
                    self.hparams.gate_threshold = 0.01
                    if message.voice == "vader:" or message.voice == "carlson:":
                        self.hparams.gate_threshold = 0.01
                        if any(char.isdigit() for char in message.text):
                            self.hparams.gate_threshold = 0.5
                    else:
                        self.hparams.gate_threshold = 0.01
                        if any(char.isdigit() for char in message.text):
                            self.hparams.gate_threshold = 0.1
                elif trimmed_message_length >= 7 and trimmed_message_length < 15:
                    self.hparams.gate_threshold = 0.1
                    if message.voice == "vader:" or message.voice == "carlson:":
                        self.hparams.gate_threshold = 0.01
                        if any(char.isdigit() for char in message.text):
                            self.hparams.gate_threshold = 0.5
                    else:
                        self.hparams.gate_threshold = 0.1
                        if any(char.isdigit() for char in message.text):
                            self.hparams.gate_threshold = 0.2
                else:
                    self.hparams.gate_threshold = 0.5

                message_extended = False
                if trimmed_message_length < 11:
                    if message.voice == "vader:":
                        message.text = "{} -. -------. -------.".format(
                            message.text)
                    else:
                        message.text = "{} -------. -------.".format(
                            message.text)
                    message_extended = True

                model = load_model(self.hparams)
                model.load_state_dict(torch.load(
                    self.models_path + self.models_22khz[message.voice])["state_dict"])
                _ = model.cuda().eval().half()

                sequence = np.array(text_to_sequence(
                    message.text, ["english_cleaners"]))[None, :]
                sequence = torch.autograd.Variable(
                    torch.from_numpy(sequence)).cuda().long()

                mel_outputs_postnet, requires_cutting = model.inference(
                    sequence)

                with torch.no_grad():
                    audio = waveglow.infer(mel_outputs_postnet, sigma=1)
                # audio_denoised = denoiser(audio, strength=0.001)[:, 0]
                # if np.isnan(audio_denoised.cpu().numpy()[0][0]):
                #     audio_data = audio.cpu().numpy()[0]
                # else:
                #     audio_data = audio_denoised.cpu().numpy()[0]
                audio_data = audio.cpu().numpy()[0]

                scaled_audio = np.int16(
                    audio_data/np.max(np.abs(audio_data)) * self.audio_length_parameter)
                if message_extended or requires_cutting:
                    cut_index = 0
                    silence_length = 0
                    for i, val in enumerate(scaled_audio):
                        if val == 0:
                            silence_length += 1
                        if silence_length > 500:
                            cut_index = i
                            break
                    scaled_audio = scaled_audio[:cut_index]
                if message.voice == "vader:":
                    _, effect = read("extras/breathing.wav")
                    scaled_audio = np.concatenate((effect, scaled_audio))

                scaled_audio = np.concatenate((scaled_audio, self.silence))
                self.joined_audio = np.concatenate(
                    (self.joined_audio, scaled_audio))
                if requires_cutting:
                    torch.cuda.empty_cache()
            else:
                engine = pyttsx3.init()
                if self.current_os == "Windows":
                    engine.setProperty(
                        "voice", self.synth_voices_windows[message.voice])
                else:
                    engine.setProperty(
                        "voice", self.synth_voices_linux[message.voice])
                engine.setProperty("rate", 120)
                engine.save_to_file(message.text, self.temp_file)
                engine.runAndWait()

                while not os.path.isfile(self.temp_file):
                    time.sleep(1.5)

                if os.path.isfile(self.temp_file):
                    del engine
                    file = read(os.path.join(
                        os.path.abspath("."), self.temp_file))
                    audio = np.array(file[1], dtype=np.int16)
                    audio = np.concatenate((audio, self.silence))
                    self.joined_audio = np.concatenate(
                        (self.joined_audio, audio))
                    os.remove(self.temp_file)

        scaled_audio = np.int16(
            self.joined_audio/np.max(np.abs(self.joined_audio)) * self.audio_length_parameter)
        if scaled_audio[0] == self.audio_length_parameter:
            scaled_audio = scaled_audio[1:]

        return scaled_audio, self.hparams.sampling_rate
