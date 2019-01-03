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

from audioprocessing.io.synthesizer import SoundSynthesizer
from audioprocessing.io.wav_file import WavFileWriter
from tst_utils import path_for_test_output

INNO_ALLA_GIOIA_MELODIA = """
B B C5 D5 D5 C5 B A G 
G A B B A A
B B C5 D5 D5 C5 B A G
G A B A G G

A A B G
A B C5 B G
A B C5 B G
G A D

B B C5 D5 D5 C5 B A G
G A B A G G 
"""

SIMPLE_TEST = """
C5 D5
"""


class SoundSynthesizerTest(unittest.TestCase):

    def test_generate_wav(self):
        synt = SoundSynthesizer(44100, 120)
        melody = synt.parse_and_generate_melody(INNO_ALLA_GIOIA_MELODIA)
        WavFileWriter(path_for_test_output("simple_test.wav")).write(melody)

