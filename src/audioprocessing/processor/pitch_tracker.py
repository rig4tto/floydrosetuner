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

import logging

logger = logging.getLogger(__name__)

DEFAULT_MAX_PITCH_DELTA_SEMITONES = 25.0/100.0


class PitchTracker(object):
    def __init__(self, max_delta=DEFAULT_MAX_PITCH_DELTA_SEMITONES):
        self.max_delta = max_delta
        self.current_pitches = {}

    def process(self, pitches, iteration, **other_signals):
        ongoing_pitches = {}
        started_pitches = {}
        for p in pitches:
            found = False
            for cp, cpv in self.current_pitches.items():
                if abs(cp.offset_from_c0 - p.offset_from_c0) < self.max_delta:
                    ongoing_pitches[cp] = cpv
                    found = True
                    break
            if not found:
                started_pitches[p] = iteration
        finished_pitches = {p: v for p,v in self.current_pitches.items() if p not in ongoing_pitches.keys()}
        self.current_pitches = {}
        self.current_pitches.update(ongoing_pitches)
        self.current_pitches.update(started_pitches)
        return {
            "started_pitches": started_pitches,
            "ongoing_pitches": ongoing_pitches,
            "finished_pitches": finished_pitches,
        }
