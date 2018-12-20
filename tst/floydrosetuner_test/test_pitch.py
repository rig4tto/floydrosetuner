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

from floydrosetuner.pitch import Pitch, MIN_FREQUENCY, MAX_FREQUENCY


class NoteTest(unittest.TestCase):
    def test_ctor_with_valid_frequncy(self):
        Pitch(440.0)

    def test_ctor_with_invalid_frequency_negative(self):
        with self.assertRaises(ValueError):
            Pitch(-1)

    def test_ctor_with_invalid_frequency_too_low(self):
        with self.assertRaises(ValueError):
            Pitch(MIN_FREQUENCY - 1)

    def test_ctor_with_invalid_frequency_too_high(self):
        with self.assertRaises(ValueError):
            Pitch(MAX_FREQUENCY + 1)

    def test_parse(self):
        self.assertEqual(440.0, Pitch.parse("A").frequency)
