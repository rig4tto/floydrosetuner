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

from ..model.pitch import Pitch

logger = logging.getLogger(__name__)

DEFAULT_FFT_RESOLUTION_HZ = 0.1
DEFAULT_FFT_MIN_ABSOLUTE_PEAK_HEIGHT = 0.0005

DEFAULT_BANDS = [
    (Pitch.parse("C3").frequency, Pitch.parse("B3").frequency),
    (Pitch.parse("C4").frequency, Pitch.parse("B4").frequency)
]
DEFAULT_MAX_FREQ_HZ = Pitch.parse("F6").frequency


class BandPeakFinder(object):
    def __init__(self, sample_rate,
                 min_absolute_peak_height=DEFAULT_FFT_MIN_ABSOLUTE_PEAK_HEIGHT,
                 fft_resolution_hz=DEFAULT_FFT_RESOLUTION_HZ,
                 bands=DEFAULT_BANDS):
        self.sample_rate = sample_rate
        self.fft_resolution_hz = fft_resolution_hz
        self.bands = bands
        self.min_absolute_peak_height = min_absolute_peak_height
        self.fft_size = int(sample_rate / fft_resolution_hz)
        self.idx_to_freq = float(sample_rate) * np.fft.fftfreq(self.fft_size)

        self.bands_idx = []
        for b in self.bands:
            min_idx = np.argmin(np.abs(self.idx_to_freq - b[0]))
            max_idx = np.argmin(np.abs(self.idx_to_freq - b[1]))
            assert b[0] < b[1]
            assert min_idx < max_idx
            self.bands_idx.append((min_idx, max_idx))
            logger.info("Band %r - %r (idx %r - %r)",
                        self.idx_to_freq[min_idx], self.idx_to_freq[max_idx], min_idx, max_idx)

    def process(self, source_signal, **other_signals):
        bands_peak = []
        if len(source_signal) > 0:
            min_peaks_height = len(source_signal) * self.min_absolute_peak_height
            logging.info("finding bands peaks for %r samples %r fft size", len(source_signal), self.fft_size)
            spectrum = np.fft.fft(source_signal, self.fft_size)
            spectrum_amp = np.abs(spectrum)
            for band in self.bands_idx:
                peak_idx = band[0] + np.argmax(spectrum_amp[band[0]:band[1]])
                peak_amp = spectrum_amp[peak_idx]
                peak_freq = self.idx_to_freq[peak_idx]
                if peak_amp < min_peaks_height:
                    peak_freq = None
                bands_peak.append(peak_freq)
        return {
            "bands_peak": bands_peak,
        }
