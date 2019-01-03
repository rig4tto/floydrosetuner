import logging
import numpy as np
from scipy.signal import find_peaks
import demo_commons as dc

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

s = np.concatenate([
    dc.generate_note(sample_rate, 0.8, 220.0, 1.0, fade_out=0.25),
    dc.generate_note(sample_rate, 0.6, 440.0, 1.0),
    dc.generate_note(sample_rate, 0.6, 90.0, 1.0),
])

# s = np.concatenate([
#     dc.generate_sin(sample_rate, 0.8, 160.5, 0.0, 1.0, 0)
# ])

i = 0
while i < len(s):
    chunk = s[i:i+processing_chunk_size]
    fft_out = np.abs(np.fft.fft(chunk, fft_size))
    fft_max = fft_out[np.argmax(fft_out)]
    min_peaks_height = fft_max * 0.3
    peaks, _ = find_peaks(fft_out, min_peaks_height)
    logging.info("peaks: %r", ["({}: {})".format(idx_to_freq[p], fft_out[p]) for p in peaks if idx_to_freq[p] >= 0])
    logging.debug("right neighbors: %r", [idx_to_freq[p+1] for p in peaks if idx_to_freq[p+1] >= 0])
    i += processing_chunk_size

logger.info("completed")
