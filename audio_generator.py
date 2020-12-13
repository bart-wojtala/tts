import os
import time
import sys
sys.path.append('tts/')
sys.path.append('tts/waveglow/')

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
    models = {
        "woman:": "tacotron2_statedict.pt",
        "david:": "attenborough_checkpoint_547000",
        "neil:": "neil_tyson_checkpoint_500000",
        "satan:": "tacotron2_statedict.pt",
        "voicemail:": "tacotron2_statedict.pt",
        "vader:": "jej_checkpoint_904500",
        "trump:": "trump_7752",
        "gandalf:": "gandalf_checkpoint_23932",
        "keanu:": "keanu_34112"
    }

    synth_voices = {
        "stephen:": "default"
    }

    waveglow = {
        "default": "waveglow_256channels.pt",
        "vader:": "jej_waveglow_165k.pt"
    }

    def __init__(self, messages):
        self.messages = messages

    def load_model(self, hparams):
        model = Tacotron2(hparams).cuda()
        if hparams.fp16_run:
            model.decoder.attention_layer.score_mask_value = finfo(
                'float16').min

        if hparams.distributed_run:
            model = apply_gradient_allreduce(model)

        return model

    def generate(self):
        hparams = create_hparams()
        hparams.sampling_rate = 22050
        models_path = "tts/models/"

        # waveglow_path = models_path + 'waveglow_256channels.pt'
        # waveglow = torch.load(waveglow_path)['model']
        # waveglow.cuda().eval().half()
        # for k in waveglow.convinv:
        #     k.float()
        # denoiser = Denoiser(waveglow)

        joined_audio = np.empty(1,)
        silence = np.zeros(11000,)
        for message in self.messages:
            if message.voice in self.models:
                waveglow_path = ''
                if message.voice == "vader:":
                    waveglow_path = models_path + self.waveglow[message.voice]
                else:
                    waveglow_path = models_path + self.waveglow['default']

                waveglow = torch.load(waveglow_path)['model']
                waveglow.cuda().eval().half()
                for k in waveglow.convinv:
                    k.float()
                denoiser = Denoiser(waveglow)

                if len(message.message) > 127:
                    hparams.max_decoder_steps = 100000
                else:
                    hparams.max_decoder_steps = 10000

                if len(message.message) < 6:
                    hparams.gate_threshold = 0.05
                elif len(message.message) >= 6 and len(message.message) < 15:
                    hparams.gate_threshold = 0.1
                else:
                    hparams.gate_threshold = 0.5

                message_extended = False
                if len(message.message) < 11:
                    message.message = message.message + " ----------------."
                    message_extended = True

                model = self.load_model(hparams)
                model.load_state_dict(torch.load(
                    models_path + self.models[message.voice])['state_dict'])
                _ = model.cuda().eval().half()

                sequence = np.array(text_to_sequence(
                    message.message, ['english_cleaners']))[None, :]
                sequence = torch.autograd.Variable(
                    torch.from_numpy(sequence)).cuda().long()

                mel_outputs, mel_outputs_postnet, _, alignments = model.inference(
                    sequence)

                with torch.no_grad():
                    audio = waveglow.infer(mel_outputs_postnet, sigma=1)
                # audio_data = audio[0].data.cpu().numpy()
                audio_denoised = denoiser(audio, strength=0.001)[:, 0]
                audio_data = audio_denoised.cpu().numpy()[0]

                # audio_data = np.concatenate((audio_data, silence))
                scaled_audio = np.int16(
                    audio_data/np.max(np.abs(audio_data)) * 32767)
                if message_extended:
                    cut_idx = 0
                    silence_length = 0
                    for idx, val in enumerate(scaled_audio):
                        if val == 0:
                            silence_length += 1
                        if silence_length > 500:
                            cut_idx = idx
                            break
                    scaled_audio = scaled_audio[:cut_idx]
                if message.voice == "vader:":
                    _, effect = read("extras/breathing.wav")
                    scaled_audio = np.concatenate((effect, scaled_audio))

                scaled_audio = np.concatenate((scaled_audio, silence))
                joined_audio = np.concatenate((joined_audio, scaled_audio))

                # torch.cuda.empty_cache()
            else:
                temp_file = 'temp.wav'
                engine = pyttsx3.init()
                engine.setProperty('voice', self.synth_voices[message.voice])
                engine.setProperty('rate', 120)
                engine.save_to_file(message.message, temp_file)
                engine.runAndWait()

                while not os.path.exists(temp_file):
                    time.sleep(1)

                if os.path.isfile(temp_file):
                    file = read(os.path.join(os.path.abspath("."), temp_file))
                    audio = np.array(file[1], dtype=np.int16)
                    audio = np.concatenate((audio, silence))
                    joined_audio = np.concatenate((joined_audio, audio))
                    os.remove(temp_file)

        scaled_audio = np.int16(
            joined_audio/np.max(np.abs(joined_audio)) * 32767)
        if scaled_audio[0] == 32767:
            scaled_audio = scaled_audio[1:]

        return scaled_audio, hparams.sampling_rate
