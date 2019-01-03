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
from scipy.io import wavfile

logger = logging.getLogger(__name__)


DEFAULT_PROCESSING_RATE = 8.0


class WavFileReader(object):
    def __init__(self, filename, processing_rate=DEFAULT_PROCESSING_RATE):
        self.filename = filename
        self.processing_rate = processing_rate
        self.sample_rate = None
        self.audio_signal = None
        self.chunk_size = None
        self.cursor = 0

    def __enter__(self):
        logger.info("Loading wav file %r", self.filename)
        self.sample_rate, self.audio_signal = wavfile.read(self.filename)
        self.chunk_size = int(self.sample_rate / self.processing_rate)
        self.processing_rate = float(self.sample_rate) / float(self.chunk_size)
        self.cursor = 0
        logger.info("Chunk size %r, expected processing rate %r",
                    self.chunk_size, self.processing_rate)
        return self

    def __exit__(self, *args):
        logger.info("WavFileReader exit context")

    def get_sample_rate(self):
        if self.sample_rate is None:
            raise ValueError("sample rate is currenlty none, open the context before using it")
        return self.sample_rate

    def eos(self):
        return not self.cursor < len(self.audio_signal)

    def read(self):
        data = []
        if self.cursor < len(self.audio_signal):
            data = self.audio_signal[self.cursor:self.cursor + self.chunk_size]
            self.cursor += self.chunk_size
        return {
            "source_signal": data,
            "sample_rate": self.sample_rate,
        }


class WavFileWriter(object):
    def __init__(self, filename, sample_rate=DEFAULT_PROCESSING_RATE):
        self.filename = filename
        self.sample_rate = sample_rate
        self.audio_signal = None

    def __enter__(self):
        logger.info("WavFileWriter initializing output signal")
        self.audio_signal = None
        return self

    def __exit__(self, *args):
        logger.info("WavFileWriter writing %r samples to %r, sample_rate=%r",
                    len(self.audio_signal), self.filename, self.sample_rate)
        wavfile.write(self.filename, self.sample_rate, self.audio_signal)

    def write(self, data):
        if self.audio_signal:
            self.audio_signal = np.concatenate([self.audio_signal, data])
        else:
            self.audio_signal = data
