import os
import platform
import time
import sys
sys.path.append('tacotron2/')
sys.path.append('tacotron2/waveglow/')

from scipy.io.wavfile import read
import pyttsx3
from denoiser import Denoiser
from text import text_to_sequence
from audio_processing import griffin_lim
from layers import TacotronSTFT, STFT
from model import Tacotron2
from hparams import create_hparams
import numpy as np
import torch
# from train import load_model


class AudioGenerator:
    models_22khz = {
        "carlson:": "tuck2",
        "carolla:": "ac2_checkpoint_637800",
        "daria:": "daria22_model",
        "david:": "attenborough_checkpoint_824800",
        "duke:": "duke_53795",
        "fergy:": "fergy-fudgehog",
        "gandalf:": "gandalf_checkpoint_23932",
        "glados:": "glados_7325",
        "hal:": "hal_9000",
        "hudson:": "hudson-horstachio-22khz",
        "keanu:": "keanu_67912",
        "mlpab:": "Apple_Bloom_28037_0.120",
        "mlpaj:": "Applejack_40071_0.156",
        "mlpbm:": "Big_Macintosh_12650_0.024",
        "mlpca:": "Celestia_38429_0.167",
        "mlpfy:": "Fluttershy_46598_0.101",
        "mlpla:": "Luna_30075_0.184",
        "mlppp:": "Pinkie_Pie_46853_0.119",
        "mlprd:": "Rainbow_Dash_62638_0.228",
        "mlpry:": "Rarity_43950_0.150",
        "mlpsb:": "Sweetie_Belle_38746_0.329_Neutral_Happy_Amused",
        "mlpse:": "Spike_32978_0.145",
        "mlpso:": "Scootaloo_24363_0.210",
        "mlpte:": "Trixie_30256_0.059",
        "mlpts:": "Twilight_Sparkle_42660_0.179",
        "mlpza:": "Zecora_8977_0.058",
        "nameless:": "Nameless.Hero_6640_g2_0.299372_22",
        "neil:": "neil_tyson_checkpoint_500000",
        "samuel:": "slj_42372",
        "satan:": "tacotron2_statedict.pt",
        "trump:": "trump_7752",
        "vader:": "jej_checkpoint_904500",
        "woman:": "tacotron2_statedict.pt",
        "vmail:": "tacotron2_statedict.pt"
    }

    synth_voices_linux = {
        "stephen:": "default"
    }

    synth_voices_windows = {
        "msdavid:": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_DAVID_11.0",
        "mszira:": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0",
        "stephen:": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\eSpeakNG_en"
    }

    waveglow_22khz = {
        "david:": "attenborough_waveglow_1516200",
        "default": "waveglow_256channels.pt",
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

    def load_model(self, hparams):
        model = Tacotron2(hparams).cuda()
        if hparams.fp16_run:
            model.decoder.attention_layer.score_mask_value = finfo(
                'float16').min

        if hparams.distributed_run:
            model = apply_gradient_allreduce(model)

        return model

    def generate(self):
        for message in self.messages:
            if message.voice in self.models_22khz:
                self.hparams.sampling_rate = self.default_sampling_rate
                waveglow_path = ''
                if message.voice == "vader:" or message.voice == "duke:":
                    waveglow_path = self.models_path + \
                        self.waveglow_22khz["vader:"]
                elif message.voice == "keanu:" or message.voice == "hal:":
                    waveglow_path = self.models_path + \
                        self.waveglow_22khz["david:"]
                else:
                    waveglow_path = self.models_path + \
                        self.waveglow_22khz['default']

                waveglow = torch.load(waveglow_path)['model']
                waveglow.cuda().eval().half()
                for k in waveglow.convinv:
                    k.float()
                denoiser = Denoiser(waveglow)

                if len(message.message) > 127:
                    self.hparams.max_decoder_steps = 100000
                else:
                    self.hparams.max_decoder_steps = 10000

                trimmed_message_length = len(
                    ''.join(c for c in message.message if c.isalnum()))
                if trimmed_message_length < 4:
                    if message.voice == "vader:":
                        self.hparams.max_decoder_steps = 1000
                        self.hparams.gate_threshold = 0.001
                        if any(char.isdigit() for char in message.message):
                            self.hparams.max_decoder_steps = 10000
                            self.hparams.gate_threshold = 0.5
                if trimmed_message_length >= 4 and trimmed_message_length < 7:
                    self.hparams.gate_threshold = 0.01
                    if message.voice == "vader:":
                        self.hparams.gate_threshold = 0.01
                        if any(char.isdigit() for char in message.message):
                            self.hparams.gate_threshold = 0.5
                    else:
                        self.hparams.gate_threshold = 0.01
                        if any(char.isdigit() for char in message.message):
                            self.hparams.gate_threshold = 0.1
                elif trimmed_message_length >= 7 and trimmed_message_length < 15:
                    self.hparams.gate_threshold = 0.1
                    if message.voice == "vader:":
                        self.hparams.gate_threshold = 0.01
                        if any(char.isdigit() for char in message.message):
                            self.hparams.gate_threshold = 0.5
                    else:
                        self.hparams.gate_threshold = 0.1
                        if any(char.isdigit() for char in message.message):
                            self.hparams.gate_threshold = 0.2
                else:
                    self.hparams.gate_threshold = 0.5

                message_extended = False
                if trimmed_message_length < 11:
                    if message.voice == "vader:":
                        message.message = message.message + " -. -------. -------."
                    else:
                        message.message = message.message + " -------. -------."
                    message_extended = True

                model = self.load_model(self.hparams)
                model.load_state_dict(torch.load(
                    self.models_path + self.models_22khz[message.voice])['state_dict'])
                _ = model.cuda().eval().half()

                sequence = np.array(text_to_sequence(
                    message.message, ['english_cleaners']))[None, :]
                sequence = torch.autograd.Variable(
                    torch.from_numpy(sequence)).cuda().long()

                mel_outputs, mel_outputs_postnet, _, alignments, requires_cutting = model.inference(
                    sequence)

                with torch.no_grad():
                    audio = waveglow.infer(mel_outputs_postnet, sigma=1)
                audio_denoised = denoiser(audio, strength=0.001)[:, 0]
                audio_data = audio_denoised.cpu().numpy()[0]

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
                # torch.cuda.empty_cache()
            else:
                temp_file = 'temp.wav'
                engine = pyttsx3.init()
                if self.current_os == 'Windows':
                    engine.setProperty(
                        'voice', self.synth_voices_windows[message.voice])
                else:
                    engine.setProperty(
                        'voice', self.synth_voices_linux[message.voice])
                engine.setProperty('rate', 120)
                engine.save_to_file(message.message, temp_file)
                engine.runAndWait()

                while not os.path.isfile(temp_file):
                    time.sleep(1.5)

                if os.path.isfile(temp_file):
                    del engine
                    file = read(os.path.join(os.path.abspath("."), temp_file))
                    audio = np.array(file[1], dtype=np.int16)
                    audio = np.concatenate((audio, self.silence))
                    self.joined_audio = np.concatenate(
                        (self.joined_audio, audio))
                    os.remove(temp_file)

        scaled_audio = np.int16(
            self.joined_audio/np.max(np.abs(self.joined_audio)) * self.audio_length_parameter)
        if scaled_audio[0] == self.audio_length_parameter:
            scaled_audio = scaled_audio[1:]

        return scaled_audio, self.hparams.sampling_rate
