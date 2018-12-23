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

from .signal import Signal


def split(signal, split_points):
    return [Signal(signal.sample_rate, signal.samples[sp[0]:sp[1]]) for sp in split_points]


def split_points_on_silence(power):
    parts = []
    pmin = min(power.samples)
    pmax = max(power.samples)
    threshold = pmin + 0.1 * (pmax - pmin)
    cursor = 0
    while cursor < len(power.samples):
        while cursor < len(power.samples) and power.samples[cursor] < threshold:
            cursor += 1
        first_noise_pos = cursor
        while cursor < len(power.samples) and power.samples[cursor] > threshold:
            cursor += 1
        if first_noise_pos < len(power.samples):
            parts.append((first_noise_pos, cursor))
    return parts
