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

from audiosignal_old.signal import Signal
import unittest


class SignalTest(unittest.TestCase):

    def test_ctor(self):
        sample_rate = 10
        samples = [0.1]
        s = Signal(sample_rate, samples)
        self.assertEquals(sample_rate, s.sample_rate)
        self.assertEquals(samples, s.samples)

    def test_ctor_with_none_sample_rate(self):
        with self.assertRaises(AssertionError):
            Signal(None, [1.0])

    def test_ctor_with_invalid_sample_rate_type(self):
        with self.assertRaises(AssertionError):
            Signal(None, [1.0])

    def test_ctor_with_invalid_sample_rate_value(self):
        with self.assertRaises(ValueError):
            Signal(0, [1.0])

    def test_ctor_with_invalid_sample_type(self):
        with self.assertRaises(AssertionError):
            Signal(10, [1])

    def test_ctor_with_invalid_sample_value(self):
        with self.assertRaises(ValueError):
            Signal(10, [1.0, 2.0])

