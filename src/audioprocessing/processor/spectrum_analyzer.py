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
from scipy.signal import find_peaks

logger = logging.getLogger(__name__)

DEFAULT_FFT_RESOLUTION_HZ = 1.0 / 4.0
DEFAULT_FFT_MIN_RELATIVE_PEAK_HEIGHT = 1.0 / 3.0
DEFAULT_FFT_MIN_ABSOLUTE_PEAK_HEIGHT = 0.001


class SpectrumAnalyzer(object):
    def __init__(self, sample_rate, fft_resolution_hz=DEFAULT_FFT_RESOLUTION_HZ,
                 min_relative_peak_height=DEFAULT_FFT_MIN_RELATIVE_PEAK_HEIGHT,
                 min_absolute_peak_height=DEFAULT_FFT_MIN_ABSOLUTE_PEAK_HEIGHT):
        self.sample_rate = sample_rate
        self.fft_resolution_hz = fft_resolution_hz
        self.min_relative_peak_height = min_relative_peak_height
        self.min_absolute_peak_height = min_absolute_peak_height
        self.fft_size = int(sample_rate / fft_resolution_hz)
        self.idx_to_freq = float(sample_rate) * np.fft.fftfreq(self.fft_size)

    def process(self, source_signal, **other_signals):
        spectrum = np.fft.fft(source_signal, self.fft_size)
        spectrum_amp = np.abs(spectrum)
        max_amp = spectrum_amp[np.argmax(spectrum_amp)]
        min_peaks_height = max(max_amp * self.min_relative_peak_height,
                               len(source_signal) * self.min_absolute_peak_height)
        peaks_idx, _ = find_peaks(spectrum_amp, min_peaks_height)
        peaks_idx = [p for p in peaks_idx if self.idx_to_freq[p] >= 0]
        peaks_freq = [self.idx_to_freq[p] for p in peaks_idx]
        return {
            "spectrum": spectrum,
            "spectrum_amp": spectrum_amp,
            "spectrum_peaks_idx": peaks_idx,
            "spectrum_peaks_freq": peaks_freq,
        }
