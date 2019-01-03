# Floyd Rose Tuner
# Copyright (C) 2019  Daniele Rigato
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import logging
from audioprocessing.model.pitch import Pitch

logger = logging.getLogger(__name__)

ZERO_TIMBRE = []
GUITAR_TIMBRE = [(2.0, 1.1), (1.5, 0.4), (4.0, 0.1)]

DEFAULT_TIMBRE = GUITAR_TIMBRE
DEFAULT_FADE_IN = 0.01
DEFAULT_FADE_OUT = 0.01


class GeneratedSoundReader(object):
    def __init__(self, sample_rate, processing_rate, beat, audio_signal_generator, default_timbre=DEFAULT_TIMBRE):
        self.synthesizer = SoundSynthesizer(sample_rate, beat, default_timbre)
        self.sample_rate = sample_rate
        self.processing_rate = processing_rate
        self.audio_signal_generator = audio_signal_generator

    def __enter__(self):
        logger.info("Generating sound")
        self.audio_signal = self.audio_signal_generator(self.synthesizer)
        if self.audio_signal is None:
            raise ValueError("None generated audio signal")
        self.chunk_size = int(self.sample_rate / self.processing_rate)
        self.processing_rate = float(self.sample_rate) / float(self.chunk_size)
        self.cursor = 0
        logger.info("Chunk size %r, expected processing rate %r",
                    self.chunk_size, self.processing_rate)
        return self

    def __exit__(self, *args):
        logger.info("GeneratedSoundReader exit context")

    def get_sample_rate(self):
        return self.sample_rate

    def eos(self):
        return not self.cursor < len(self.audio_signal)

    def read(self):
        data = []
        if self.cursor < len(self.audio_signal):
            data = self.audio_signal[self.cursor:self.cursor + self.chunk_size]
            self.cursor += self.chunk_size
        return {
            "source_signal": data,
        }


def create_melody_generator(melody_str, timbre=None, fade_in=DEFAULT_FADE_IN, fade_out=DEFAULT_FADE_OUT):
    def melody_generator(synthesizer):
        return synthesizer.parse_and_generate_melody(melody_str, timbre, fade_in, fade_out)
    return melody_generator


class SoundSynthesizer(object):
    def __init__(self, sample_rate, beat, default_timbre=DEFAULT_TIMBRE):
        self.sample_rate = sample_rate
        self.beat = beat
        self.default_timbre = default_timbre

    def value_to_duration(self, value):
        return value * 4.0 * 60.0 / self.beat

    def generate_t(self, duration, start=0.0):
        return start + np.arange(0.0, float(duration) * float(self.sample_rate), dtype=np.float32) / float(self.sample_rate)

    def generate_sin(self, amp, freq, phase, duration, start=0.0):
        t_signal = self.generate_t(duration=duration, start=start)
        s = amp * np.sin(2.0 * np.pi * float(freq) * t_signal + float(phase))
        return s

    def generate_fade(self, duration, fade_in, fade_out):
        fade_in_signal = []
        if fade_in > 0.0:
            fade_in_signal = np.arange(0.0, 1.0, 1.0 / (float(fade_in) * float(self.sample_rate)), dtype=np.float32)
        fade_out_signal = []
        if fade_out > 0.0:
            fade_out_signal = np.arange(1.0, 0.0, - 1.0 / (float(fade_out) * float(self.sample_rate)), dtype=np.float32)
        left_over = int(duration * self.sample_rate) - len(fade_in_signal) - len(fade_out_signal)
        if left_over > 0:
            left_over_signal = np.ones(left_over, dtype=np.float32)
            return np.concatenate([fade_in_signal, left_over_signal, fade_out_signal])
        else:
            raise ValueError("fade is too long")

    def generate_note(self, amp, freq, value, timbre=None, fade_in=DEFAULT_FADE_IN, fade_out=DEFAULT_FADE_OUT):
        if timbre is None:
            timbre = self.default_timbre
        duration = self.value_to_duration(value)
        s = self.generate_sin(1.0, freq, 0.0, duration)
        for overtone, overtone_amp in timbre:
            s += self.generate_sin(overtone_amp, freq * overtone, 0.0, duration)
        s = amp * self.normalize(s) * self.generate_fade(duration, fade_in, fade_out)
        return s

    def generate_melody(self, notes, timbre=None, fade_in=DEFAULT_FADE_IN, fade_out=DEFAULT_FADE_OUT):
        if timbre is None:
            timbre = self.default_timbre
        return np.concatenate([self.generate_note(amp, freq, value, timbre, fade_in, fade_out)
                               for amp, freq, value in notes])

    def parse_and_generate_melody(self, melody_str, timbre=None, fade_in=DEFAULT_FADE_IN, fade_out=DEFAULT_FADE_OUT):
        if timbre is None:
            timbre = self.default_timbre
        tokens = melody_str.split()  # all whitespaces including tabs and newline
        last_amp = 0.5
        last_value = 1.0 / 4.0
        notes = []
        for token in tokens:
            try:
                notes.append((last_amp, Pitch.parse(token).frequency, last_value))
            except ValueError:
                pass
        return self.generate_melody(notes, timbre, fade_in, fade_out)

    @staticmethod
    def normalize(audio_signal):
        # the new signal is between -1 and 1
        amp = np.ptp(audio_signal)
        if amp > 0.000001:
            return (audio_signal - np.min(audio_signal)) * 2.0 / np.ptp(audio_signal) - 1.0
        else:
            logger.warning("normalize does not work with a constant audio signal")
            return audio_signal
