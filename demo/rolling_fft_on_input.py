import logging
import numpy as np
from scipy.signal import find_peaks
import sounddevice as sd
from floydrosetuner.pitch import Pitch

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# PARAMETERS
sample_rate = 44100
processing_freq = 8.0
fft_resolution_hz = 1.0 / 4.0


# PROCESSING
logger.info("starting")

fft_size = int(sample_rate / fft_resolution_hz)
processing_chunk_size = int(sample_rate / processing_freq)
idx_to_freq = float(sample_rate) * np.fft.fftfreq(fft_size)
fft_threshold = 30

with sd.Stream(channels=1, dtype=np.float32, samplerate=sample_rate) as stream:
    while True:
        indata, overflowed = stream.read(processing_chunk_size)
        chunk = indata[:, 0]
        if overflowed:
            logger.warning("overflowed while reading from sound card")
        fft_out = np.abs(np.fft.fft(chunk, fft_size))
        fft_max = fft_out[np.argmax(fft_out)]
        min_peaks_height = fft_max * 0.3
        peaks, _ = find_peaks(fft_out, min_peaks_height)
        peaks = [p for p in peaks if idx_to_freq[p] >= 0 and fft_out[p]>fft_threshold]
        if peaks:
            pitches = [Pitch(p) for p in peaks]
            logging.info("pitches: %r", [p for p in pitches])
            logging.debug("peaks: %r", ["({}: {})".format(idx_to_freq[p], fft_out[p]) for p in peaks])

logger.info("completed")
