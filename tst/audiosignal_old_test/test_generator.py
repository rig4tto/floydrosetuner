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

from audiosignal_old.generator import *


class GeneratorTest(unittest.TestCase):

    def test_sin_wave_with_no_duration(self):
        amplitude = 0.8
        freq_hz = 100
        phase = math.pi / 2.0
        sample_rate = 8000
        expected_length = int(sample_rate / freq_hz)
        s = sin_wave(amplitude, freq_hz, phase, sample_rate)

        self.assertEquals(sample_rate, s.sample_rate)
        self.assertEquals(expected_length, len(s.samples))
        self.assertEquals(amplitude, s.samples[0])
        self.assertAlmostEquals(0.0, s.samples[int(expected_length * 1/4)], delta=0.001)
        self.assertAlmostEquals(-amplitude, s.samples[int(expected_length * 2/4)], delta=0.001)
        self.assertAlmostEquals(0.0, s.samples[int(expected_length * 3/4)], delta=0.001)
        self.assertAlmostEquals(amplitude, s.samples[expected_length-1], delta=0.01)

    def test_sin_wave_with_duration(self):
        amplitude = 0.8
        freq_hz = 100
        phase = math.pi / 2.0
        sample_rate = 8000
        duration_sec = 0.5
        expected_length = sample_rate * duration_sec
        period = int(sample_rate / freq_hz)
        s = sin_wave(amplitude, freq_hz, phase, sample_rate, duration=duration_sec)

        self.assertEquals(sample_rate, s.sample_rate)
        self.assertEquals(expected_length, len(s.samples))
        self.assertEquals(amplitude, s.samples[0])
        self.assertAlmostEquals(0.0, s.samples[int(period * 1/4)], delta=0.001)
        self.assertAlmostEquals(-amplitude, s.samples[int(period * 2/4)], delta=0.001)
        self.assertAlmostEquals(0.0, s.samples[int(period * 3/4)], delta=0.001)
        self.assertAlmostEquals(amplitude, s.samples[period], delta=0.001)
