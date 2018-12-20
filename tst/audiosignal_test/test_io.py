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
from unittest.mock import call, patch, mock_open
from tst_utils import *

import math

from audiosignal.io import *

TEST_SIGNAL = Signal(sample_rate=44100, samples=[0.0, 0.1, 0.2, 0.43])

TEST_SIGNAL_FILE = """44100
0.0
0.1
0.2
0.43
"""


class WaveTest(unittest.TestCase):

    def test_unsigned_to_signed_int_8bit_correct(self):
        self.assertEquals(127, unsigned_to_signed_int(127, 1))

    def test_unsigned_to_signed_int_8bit_min_value(self):
        self.assertEquals(-128, unsigned_to_signed_int(128, 1))

    def test_unsigned_to_signed_int_8bit_to_complement(self):
        self.assertEquals(-2, unsigned_to_signed_int(254, 1))

    def test_unsigned_to_signed_int_16bit_correct(self):
        self.assertEquals(126, unsigned_to_signed_int(126, 2))

    def test_unsigned_to_signed_int_16bit_min_value(self):
        self.assertEquals(-32768, unsigned_to_signed_int(32768, 2))

    def test_unsigned_to_signed_int_16bit_to_complement(self):
        self.assertEquals(-1, unsigned_to_signed_int(65535, 2))

    def test_frame_to_float_pos0(self):
        self.assertEquals(1.0/(128*256**2), frame_to_float([1, 0, 0], 0, 3))

    def test_frame_to_float_pos1(self):
        self.assertEquals(1.0/(128*256**2), frame_to_float([2, 3, 4, 1, 0, 0], 1, 3))

    def test_frame_to_float_all_digits(self):
        self.assertEquals((1.0 + 2.0*256 + 3.0*256*256)/(128*256**2), frame_to_float([1, 2, 3], 0, 3))

    def test_load(self):
        test_file = path_for_audio_sample("sin100hz1PeriodSigned16Bit.wav")
        expected_frequency_hz = 100
        expected_sample_rate = 44100
        expected_length = int(expected_sample_rate / expected_frequency_hz)
        s = load_wav(test_file)
        self.assertEquals(expected_sample_rate, s.sample_rate)
        self.assertEquals(expected_length, len(s.samples))
        self.assertEquals(0, s.samples[0])
        omega = 2 * math.pi * expected_frequency_hz
        for i in range(0, expected_length):
            t = i/expected_sample_rate
            self.assertAlmostEquals(math.sin(omega * t), s.samples[i], delta=0.001)

    def test_dump_signal(self):
        with patch("audiosignal.io.open", mock_open(), create=True) as mock_file:
            dump_signal(TEST_SIGNAL, "/path/to/test.signal")
            mock_file.assert_called_once_with("/path/to/test.signal", "w")
            expected_calls = [call(["{}\n".format(TEST_SIGNAL.sample_rate)]),
                               call(["{}\n".format(s) for s in TEST_SIGNAL.samples])]
            self.assertEquals(expected_calls, mock_file.return_value.writelines.mock_calls)

    def test_load_signal(self):
        with patch("audiosignal.io.open", mock_open(read_data=TEST_SIGNAL_FILE), create=True) as mock_file:
            signal = load_signal("/path/to/test.signal")
            mock_file.assert_called_once_with("/path/to/test.signal", "r")
            self.assertEquals(TEST_SIGNAL.sample_rate, signal.sample_rate)
            self.assertEquals(TEST_SIGNAL.samples, signal.samples)
