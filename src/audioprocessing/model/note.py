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

"""Represents a pitch, e.g. a musical tone whose only relevant attribute is the frequency.

https://en.wikipedia.org/wiki/Musical_tone
https://en.wikipedia.org/wiki/Pitch_(music)
"""


class Note(object):
    """Represents a note, with a pitch and a start and end point in time
    """

    def __init__(self, pitch, start_s, end_s, bpm=None):
        self.pitch = pitch
        self.start_s = start_s
        self.end_s = end_s
        self.start_beat = None
        self.end_beat = None
        self.value = None
        if bpm is not None:
            self.start_beat = float(self.start_s) * float(bpm) / 60.0
            self.end_beat = float(self.end_s) * float(bpm) / 60.0
            self.value = self.end_beat - self.start_beat

    def __repr__(self):
        if self.start_beat and self.end_beat and self.value:
            s = "at beat {}:  {}{}({})  value {} beats".format(self.start_beat, self.pitch.note, self.pitch.octave, self.pitch.offset_from_c0, self.value)
        else:
            s = "{}{} from {}s to {}s".format(self.pitch.note, self.pitch.octave, self.start_s, self.end_s)
        if abs(self.pitch.error_in_semitones) >= 0.01:
            s += " - pitch err {}/100".format(int(self.pitch.error_in_semitones * 100.0))
        return s
