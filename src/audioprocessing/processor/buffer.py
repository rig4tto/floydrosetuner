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
import numpy as np


logger = logging.getLogger(__name__)


class Buffer(object):
    def __init__(self, sample_rate, buffer_duration):
        self.sample_rate = sample_rate
        self.buffer_len = int(buffer_duration * sample_rate)
        self.buffer_duration = float(self.buffer_len) / float(sample_rate)
        self.buffered_signal = None
        self.buffered_signal_start = 0

    def process(self, source_signal, **other_signals):
        if source_signal is None or len(source_signal) == 0:
            logger.warning("empty source signal")
            return {}
        if self.buffered_signal is None:
            self.buffered_signal = source_signal
        else:
            self.buffered_signal = np.concatenate([self.buffered_signal, source_signal])

        overflow = len(self.buffered_signal) - self.buffer_len
        if overflow >= 0:
            self.buffered_signal = self.buffered_signal[overflow:]
            self.buffered_signal_start += overflow

        return {
            "buffered_signal": self.buffered_signal,
            "buffered_signal_start": self.buffered_signal_start
        }
