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

from ..model.pitch import Pitch, FREQ_C0

logger = logging.getLogger(__name__)

DEFAULT_FFT_RESOLUTION_HZ = 1.0
DEFAULT_RELATIVE_MIN_POWER = 0.3
DEFAULT_ABSOLUTE_MIN_POWER = 50


class HarmonyAnalyzer(object):
    def __init__(self, sample_rate,
                 fft_resolution_hz=DEFAULT_FFT_RESOLUTION_HZ,
                 absolute_min_power=DEFAULT_ABSOLUTE_MIN_POWER,
                 relative_min_power=DEFAULT_RELATIVE_MIN_POWER):
        self.sample_rate = sample_rate
        self.relative_min_power = relative_min_power
        self.absolute_min_power = absolute_min_power
        self.fft_resolution_hz = fft_resolution_hz
        self.fft_size = int(sample_rate / fft_resolution_hz)
        self.idx_to_freq = float(sample_rate) * np.fft.fftfreq(self.fft_size)
        self.idx_to_semitones_from_c0 = np.log2(self.idx_to_freq/FREQ_C0) * 12.0
        self.idx_to_semitone_idx = (self.idx_to_semitones_from_c0 + 0.5) % 12 - 0.5
        self.semitone_masks = [np.where(float(i) - 0.1 <= self.idx_to_semitone_idx, 1, 0) *
                               np.where(self.idx_to_semitone_idx <= float(i) + 0.1, 1, 0) *
                               np.where(12 * 2 <= self.idx_to_semitones_from_c0, 1, 0) *
                               np.where(self.idx_to_semitones_from_c0 <= 12 * 6, 1, 0)
                               for i in range(12)]

    def process(self, source_signal, **other_signals):
        if len(source_signal) > 0:
            logging.debug("finding computing fft for %r samples, size %r", len(source_signal), self.fft_size)
            spectrum = np.fft.fft(source_signal, self.fft_size)
            spectrum_amp = np.abs(spectrum)
            semitone_power = [np.sum(spectrum_amp * mask) for mask in self.semitone_masks]
            max_power = np.max(semitone_power)
            semitone_relative_power = semitone_power / max_power
            powerful_semitones = [Pitch.from_octave_semitone(0, i)
                                  for i in range(len(semitone_relative_power))
                                  if semitone_relative_power[i] >= self.relative_min_power
                                  and semitone_power[i] >= self.absolute_min_power]
        else:
            semitone_power = [0.0] * 12
            semitone_relative_power = semitone_power
            powerful_semitones = []
        return {
            "semitone_power": semitone_power,
            "semitone_relative_power": semitone_relative_power,
            "powerful_semitones": powerful_semitones
        }
