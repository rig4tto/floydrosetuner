# Floyd Rose Tuner
# Copyright (C) 2018  Daniele Rigato
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

import unittest
from tst_utils import *

from audiosignal.processor import sin_wave
from audiosignal.processor import *
from audiosignal.io import load_wav, dump_signal

logging.basicConfig(level=logging.INFO)


class ProcessorTest(unittest.TestCase):

    def test_power(self):
        signal = load_wav(path_for_audio_sample("sin440_1sec.wav"))
        processor = open_string_guitar_signal_processor(signal.sample_rate)
        signal_pow = processor.power(signal)
        dump_signal(signal_pow, path_for_test_output("power_sin440_1sec.samples"))

    def test_fast_power(self):
        signal = load_wav(path_for_audio_sample("cmaj_scale.wav"))
        processor = open_string_guitar_signal_processor(signal.sample_rate)
        signal_pow = processor.fast_power(signal, 0.1)
        dump_signal(signal_pow, path_for_test_output("power_cmaj_scale.samples"))

    def test_to_freq_domain(self):
        signal = load_wav(path_for_audio_sample("sin440_1sec.wav"))
        # signal = sin_wave(0.6, 100.0, math.pi/3, 44100, 0.3)
        processor = SignalProcessor(signal.sample_rate)
        amplitude, phase = processor.to_freq_domain(signal, freq_step=10)
        logging.info("energy in frequencies: %r", processor.energetic_frequencies(amplitude))
        dump_signal(amplitude, path_for_test_output("freq_sin440_1sec.samples"))

