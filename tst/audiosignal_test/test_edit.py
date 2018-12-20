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

from audiosignal.edit import *
from audiosignal.processor import open_string_guitar_signal_processor
from audiosignal.io import load_wav, dump_signal

logging.basicConfig(level=logging.INFO)

class EditTest(unittest.TestCase):

    def test_fast_power(self):
        signal = load_wav(path_for_audio_sample("cmaj_scale.wav"))
        processor = open_string_guitar_signal_processor(signal.sample_rate)
        signal_power = processor.fast_power(signal, 0.01)
        # signal_power = processor.power(signal)

        expected_sound_parts = 8
        expected_silence_parts = 8
        expected_tot_parts = expected_sound_parts + expected_silence_parts
        expected_part_len = len(signal.samples) / expected_tot_parts

        split_points = split_points_on_silence(signal_power)
        parts = split(signal, split_points)
        for i in range(0, len(parts)):
            dump_signal(parts[i], path_for_test_output("power_cmaj_scale_part_{}.samples".format(i)))
        self.assertEqual(8, len(parts))
        self.assertEqual(8, len(split_points))
        split_seconds = [(p[0]/signal.sample_rate, p[1]/signal.sample_rate) for p in split_points]
        expected_split_points = [(2*i*expected_part_len, (2*i+1)*expected_part_len)
                                 for i in range(0, expected_sound_parts)]
        expected_split_seconds = [(p[0]/signal.sample_rate, p[1]/signal.sample_rate) for p in expected_split_points]
        max_delta = 0.05
        for i in range(len(split_seconds)):
            if abs(split_seconds[i][0] - expected_split_seconds[i][0]) > max_delta:
                logging.error("%d - start expected %r found %r", i, expected_split_seconds[i][0], split_seconds[i][0])
            if abs(split_seconds[i][1] - expected_split_seconds[i][1]) > max_delta:
                logging.error("%d - end expected %r found %r", i, expected_split_seconds[i][1], split_seconds[i][1])

        max_begin_err = max(abs(split_seconds[i][0] - expected_split_seconds[i][0]) for i in range(len(split_seconds)))
        max_end_err = max(abs(split_seconds[i][1] - expected_split_seconds[i][1]) for i in range(len(split_seconds)))
        self.assertLess(max_begin_err, max_delta)
        self.assertLess(max_end_err, max_delta)

