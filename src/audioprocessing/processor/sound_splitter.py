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

DEFAULT_MIN_NOISE_POWER = 0.01
DEFAULT_MIN_SOUND_DURATION = 0.5


class SoundSplitter(object):
    def __init__(self, min_noise_power=DEFAULT_MIN_NOISE_POWER, min_sound_duration=DEFAULT_MIN_SOUND_DURATION):
        self.min_noise_power = min_noise_power
        self.quiete = True
        self.sound_start = None
        self.min_sound_duration = min_sound_duration

    def process(self, rms, buffered_signal, buffered_signal_start, current_sample, sample_rate, **other_signals):
        split_sound = []
        sounds_split_points = []
        power = np.mean(rms)
        logger.debug("power: %r", power)
        if power > self.min_noise_power:
            if self.sound_start is None:
                self.sound_start = current_sample
        else:
            if self.sound_start is not None:
                n_samples = current_sample - self.sound_start
                duration = float(n_samples) / float(sample_rate)
                if duration > self.min_sound_duration:
                    sounds_split_points.append((self.sound_start, current_sample))
                    split_sound = buffered_signal[self.sound_start-buffered_signal_start:]
                self.sound_start = None
        return {
            "split_sound": split_sound,
            "sounds_split_points": sounds_split_points,
        }
