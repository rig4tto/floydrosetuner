import logging
import sounddevice as sd
import numpy as np

logger = logging.getLogger(__name__)


DEFAULT_SAMPLE_RATE = 44100
DEFAULT_AUDIO_FORMAT = np.float32
DEFAULT_PROCESSING_RATE = 20
DEFAULT_BUFFER_SEC = 1


class AudioStream(object):
    def __init__(self, sample_rate=DEFAULT_SAMPLE_RATE, audio_format=DEFAULT_AUDIO_FORMAT,
                 processing_rate=DEFAULT_PROCESSING_RATE, buffer_sec=DEFAULT_BUFFER_SEC):
        self.sample_rate = sample_rate
        self.audio_format = audio_format
        self.buffer_sec = buffer_sec
        self.buffer_len = int(buffer_sec * sample_rate)
        self.chunk_size = int(sample_rate / processing_rate)
        self.processing_rate = float(sample_rate) / float(self.chunk_size)
        self.stream = sd.Stream(channels=1, dtype=audio_format, samplerate=sample_rate)
        self.buffer = np.zeros(self.buffer_len, audio_format)
        logger.info("chunk size %r, expected processing rate %r", self.chunk_size, self.processing_rate)

    def __enter__(self):
        self.stream.__enter__()
        return self

    def __exit__(self, *args):
        self.stream.__exit__(*args)

    def read(self):
        indata, overflowed = self.stream.read(self.chunk_size)
        single_channel_in_data = indata[:, 0]
        if len(indata[:, 0]) > 0:
            self.buffer = np.concatenate((self.buffer, single_channel_in_data))[len(single_channel_in_data):]
        if overflowed:
            logger.warning("overflowed while reading from sound card")
        return indata

    def write(self, data):
        underflowed = self.stream.write(data)
        if underflowed:
            logger.warning("underflowed while writing to sound card")
