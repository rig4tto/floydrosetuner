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

from ..model.pitch import Pitch
from ..model.note import Note


logger = logging.getLogger(__name__)


DEFAULT_BPM = 60.0
DEFAULT_RESOLUTION_BEAT = 1.0 / 4.0 # 1 beat = 1/4, 1/4 beat = 1/16 at bpm
DEFAULT_OPTIMIZATION_FFT_RESOLUTION = 0.05
DEFAULT_SEARCH_WIN_SIZE_HZ = 2.0
DEFAULT_USE_LONG_FFT_OPTIMIZATION = True


class NoteTracker(object):
    def __init__(self, bpm=DEFAULT_BPM, resolution_beat=DEFAULT_RESOLUTION_BEAT,
                 fft_resolution_hz=DEFAULT_OPTIMIZATION_FFT_RESOLUTION,
                 search_win_size=DEFAULT_SEARCH_WIN_SIZE_HZ,
                 use_long_fft_optimization=DEFAULT_USE_LONG_FFT_OPTIMIZATION):
        self.bpm = bpm
        self.resolution_beat = resolution_beat
        self.fft_resolution_hz = fft_resolution_hz
        self.search_win_size = search_win_size
        self.use_long_fft_optimization = use_long_fft_optimization

    def process(self, finished_pitches, current_sample, sample_rate, **other_signals):
        notes = []
        if finished_pitches and len(finished_pitches) > 0:
            for p, start in finished_pitches.items():
                note = Note(pitch=p,
                            start_s=float(start) / float(sample_rate),
                            end_s=float(current_sample) / float(sample_rate),
                            bpm=self.bpm)
                if note.value > self.resolution_beat:
                    if self.use_long_fft_optimization:
                        if "buffered_signal" in other_signals:
                            note = self.long_dft_optimization(note, start, current_sample,
                                                              sample_rate,
                                                              other_signals["buffered_signal"],
                                                              other_signals["buffered_signal_start"])
                        else:
                            logger.warning("no buffered_signal, can't optimize note")
                    notes.append(note)
        return {
            "notes": notes,
        }

    def long_dft_optimization(self, note, start, current_sample, sample_rate, buffered_signal, buffered_signal_start):

            fft_size = int(sample_rate / self.fft_resolution_hz)
            buffer_start = max(0,
                               start - buffered_signal_start)
            buffer_chunk = buffered_signal[buffer_start:]
            buffer_chunk = buffer_chunk[int(len(buffer_chunk)*1/6):int(len(buffer_chunk)*4/6)]
            fft_size = max(fft_size, len(buffer_chunk))

            logging.info("optimizing on %r samples with fft size %r, resolution %r",
                         len(buffer_chunk), fft_size, self.fft_resolution_hz)

            idx_to_freq = float(sample_rate) * np.fft.fftfreq(fft_size)
            search_idx = [i for i in range(len(idx_to_freq))
                          if abs(idx_to_freq[i] - note.pitch.frequency) < self.search_win_size]
            search_win_min = np.min(search_idx)
            search_win_max = np.max(search_idx)
            spectrum_portion = np.fft.fft(buffer_chunk, fft_size)[search_win_min:search_win_max]
            spectrum_portion_amp = np.abs(spectrum_portion)
            max_freq = idx_to_freq[search_win_min + np.argmax(spectrum_portion_amp)]
            return (Note(pitch=Pitch(max_freq),
                         start_s=float(start) / float(sample_rate),
                         end_s=float(current_sample) / float(sample_rate),
                         bpm=self.bpm))

