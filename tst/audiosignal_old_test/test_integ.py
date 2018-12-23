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

import logging
import unittest
from tst_utils import *

from audiosignal_old.edit import *
from audiosignal_old.processor import *
from audiosignal_old.io import load_wav, dump_signal

logging.basicConfig(level=logging.INFO)

class IntegTest(unittest.TestCase):

    def test_split_and_analyse(self):
        signal = load_wav(path_for_audio_sample("cmaj_scale.wav"))
        processor = SignalProcessor(signal.sample_rate)
        # processor = open_string_guitar_signal_processor(signal.sample_rate)
        signal_power = processor.fast_power(signal, 0.01)
        # signal_power = processor.power(signal)
        split_points = split_points_on_silence(signal_power)
        parts = split(signal, split_points)
        for i in range(0, len(parts)):
            # cut_point = int(len(parts[i].samples)/2)
            # parts[i].samples = parts[i].samples[cut_point:cut_point+8000]
            amplitude, phase = processor.to_freq_domain(parts[i], freq_step=1)
            logging.info("energy in frequencies for part %d: %r", i, processor.energetic_frequencies(amplitude))
