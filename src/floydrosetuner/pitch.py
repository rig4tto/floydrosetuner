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

"""Represents a pitch, e.g. a musical tone whose only relevant attribute is the frequency.

https://en.wikipedia.org/wiki/Musical_tone
https://en.wikipedia.org/wiki/Pitch_(music)
"""

import math
import re

NOTE_REGEX = '([ABCDEFG])([#b]?)([0-9]?)'

SEMITONE_TO_NOTE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

#: Mapping from standard note name to the semitone starting from C=0
NOTE_TO_SEMITONE = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "B": 11,
}

#: Minimum valid frequency, no pitch can have a frequency lower than this
MIN_FREQUENCY = 0

#: Maximum valid frequency, no pitch can have a frequency greater than this
MAX_FREQUENCY = 20000

FREQ_A4 = 440.0
FREQ_C0 = FREQ_A4 * 2.0 ** (-4-(9.0/12.0))

STD_OCTAVE = 4


class Pitch(object):
    """Represents a pitch, e.g. a musical tone whose only relevant attribute is the frequency.
    """

    def __init__(self, frequency):
        """
        :param frequency: frequency measured in hertz
        :type frequency: float
        :rtype Pitch
        """
        if frequency < MIN_FREQUENCY or frequency > MAX_FREQUENCY:
            raise ValueError("invalid frequency {} valid range[{}, {}]".format(frequency, MIN_FREQUENCY, MAX_FREQUENCY))
        self.frequency = frequency
        self.offset_from_c0 = math.log(frequency/FREQ_C0, 2.0) * 12.0
        self.idx = int(round(self.offset_from_c0))
        self.octave = int(self.idx / 12.0)
        self.semitone = int(self.idx - self.octave * 12.0)
        self.note = SEMITONE_TO_NOTE[self.semitone]
        self.nominal_frequency = Pitch.frequency_from_octave_semitone(self.octave, self.semitone)
        self.error = frequency - self.nominal_frequency

    @staticmethod
    def from_octave_semitone(octave, semitone):
        return Pitch(Pitch.frequency_from_octave_semitone(octave, semitone))

    @staticmethod
    def frequency_from_octave_semitone(octave, semitone):
        return FREQ_C0 * 2.0 ** (float(octave) + float(semitone) / 12.0)

    def __repr__(self):
        s = "{}{}".format(self.note, self.octave)
        if abs(self.error) > 0.001:
            s += " err {} Hz".format(self.error)
        return s

    @staticmethod
    def _re_groups_to_pitch(groups):
        semitone = NOTE_TO_SEMITONE[groups[0]]
        alteration_flag = groups[1]
        if alteration_flag == '#':
            semitone += 1
        elif alteration_flag == 'b':
            semitone -= 1
        octave = groups[2]
        if not octave:
            octave = STD_OCTAVE
        octave = int(octave)
        return Pitch.from_octave_semitone(octave, semitone)

    @staticmethod
    def parse(my_str):
        note_match = re.match(NOTE_REGEX, my_str)
        if note_match:
            return Pitch._re_groups_to_pitch(note_match.groups())
        raise ValueError("%s is not a valid note".format(my_str))

    @staticmethod
    def parse_all(my_str):
        note_matches = re.findall(NOTE_REGEX, my_str)
        return [Pitch._re_groups_to_pitch(m) for m in note_matches]

