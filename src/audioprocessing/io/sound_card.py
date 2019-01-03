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
import sounddevice as sd
import numpy as np

logger = logging.getLogger(__name__)


DEFAULT_SAMPLE_RATE = 44100
DEFAULT_AUDIO_FORMAT = np.float32
DEFAULT_PROCESSING_RATE = 8.0


class SoundCard(object):
    def __init__(self, sample_rate=DEFAULT_SAMPLE_RATE, audio_format=DEFAULT_AUDIO_FORMAT,
                 processing_rate=DEFAULT_PROCESSING_RATE):
        self.sample_rate = sample_rate
        self.audio_format = audio_format
        self.chunk_size = int(sample_rate / processing_rate)
        self.processing_rate = float(sample_rate) / float(self.chunk_size)
        self.stream = sd.Stream(channels=1, dtype=audio_format, samplerate=sample_rate)
        self.is_open = False

    def eos(self):
        return not self.is_open

    def get_sample_rate(self):
        return self.sample_rate

    def __enter__(self):
        logger.info("Opening sound card for I/O. Chunk size %r, expected processing rate %r",
                    self.chunk_size, self.processing_rate)
        self.stream.__enter__()
        self.is_open = True
        return self

    def __exit__(self, *args):
        self.is_open = False
        self.stream.__exit__(*args)
        logger.info("Sound card closed")

    def read(self):
        input_data, overflowed = self.stream.read(self.chunk_size)
        first_channel = input_data[:, 0]
        if overflowed:
            logger.warning("Overflowed while reading from sound card (%r)", overflowed)
        return {
            "sample_rate": self.sample_rate,
            "source_signal": first_channel,
            "source_signal_all_channels": input_data,
        }

    def write(self, data):
        underflowed = self.stream.write(data)
        if underflowed:
            logger.warning("Underflowed while writing to sound card (%r)", underflowed)
