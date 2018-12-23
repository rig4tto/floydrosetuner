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

import math
from .signal import Signal


def sin_wave(amplitude, freq, phase, sample_rate, duration=None):
    if duration is None:
        # equal to the period T = 1/freq [s]
        duration = 1 / freq
    n_samples = int(duration * sample_rate)
    omega = 2.0 * math.pi * freq
    samples = [amplitude * math.sin(phase + omega * float(i) / float(sample_rate))
               for i in range(0, n_samples)]
    return Signal(sample_rate=sample_rate, samples=samples)
