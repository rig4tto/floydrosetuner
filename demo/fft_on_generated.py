import logging
import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt

import demo_commons as dc

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# PARAMETERS

sample_rate = 44100
fft_resolution_hz = 1.0

# PROCESSING
logger.info("starting")

logger.info("""
The fourier transform rfft on a real signal of length N returns about N/2+1 samples (exactly if N is even, i.e. N%2==0)
To understand to which frequencies they corresponds, imagine the signal is samples at 1Hz (one sample per second).
If N=1, you can know only the continuous component f=0 of the signal, hence rfftfreq(1) = [0]
If N=2, you have 2 samples and you can know the difference between s[0] and s[1], that difference let you compute
f=0.2Hz (T=2). In general you need to have N>T to estimate f=1/T. The higher is N, the longer is the max T, the more
resolution you have in the frequency domain.

The difference from one frequency to the next is always the same, they are equally distant. The distance (or resolution)
is equal to 1/N. Indeed, if N is even, you can compute rfftfreq as [float(i)*float(1/N) for i in range(0, N/2)].

The highest frequency is 0.5 = sample rate (1Hz) / 2 (Nyquist freq.). Indeed, if you have one sample per second, 
you can't distinguish a constant form a 1Hz sin, or k Hz sin.
""")

logging.info("rfftfreq(1) = %r", np.fft.rfftfreq(1))
logging.info("rfftfreq(2) = %r", np.fft.rfftfreq(2))
logging.info("rfftfreq(4) = %r", np.fft.rfftfreq(4))
logging.info("rfftfreq(8) = %r", np.fft.rfftfreq(8))
logging.info("rfftfreq(10) = %r", np.fft.rfftfreq(10))

logging.info("""
If the sample rate is different from 1Hz, the same apply multiplying everyting by the sample rate
""")

logging.info("sample rate =   1 Hz, N=4, frequencies = %r", 1 * np.fft.rfftfreq(4))
logging.info("sample rate =  10 Hz, N=4, frequencies = %r", 10 * np.fft.rfftfreq(4))
logging.info("sample rate = 100 Hz, N=4, frequencies = %r", 100 * np.fft.rfftfreq(4))

logging.info("""
Hence, the longest the signal, the more samples you have, the highest the resolution in the frequency domain is.
This is expected since you know more about the signal. This is the first limitation.
""")

logging.info("""
The FFT works great (i.e. it produces a nice output easy to interpret) for periodic signals when N is a multiple of 
T. This highlight the second limitation: to have a clear output you must know the period T of the signal and 
you must have enough samples.
""")













logging.info("""
Example 1: N = 10, f = 1/10 => f(0.1) = 5 = N/2, all the other freqs = 0
""")

s = dc.generate_sin(sample_rate=1, amp=1, freq=0.1, phase=0.0, duration=10.0, start=0.0)
f = np.fft.rfftfreq(len(s))
f_amp = np.abs(np.fft.rfft(s))
plt.plot(f, f_amp, 'r+')
plt.show()

logging.info("""
Example 2: N = 100, f = 1/10 => f(0.1) = 50 = N/2, all the other freqs = 0
""")

s = dc.generate_sin(sample_rate=1, amp=1, freq=0.1, phase=0.0, duration=100.0, start=0.0)
f = np.fft.rfftfreq(len(s))
f_amp = np.abs(np.fft.rfft(s))
plt.plot(f, f_amp, 'r+')
plt.show()

logging.info("""
Example 3: N = 11, f = 1/10 => There is still a spike at 0.0909 near 0.1, but the other frequencies are > 0 as well,
around 0.8 (1/5 of the spike). The closer to 0.1, the higher their value, although the difference between the closer and
the farest is not that much (0.8 vs 0.3).

Note that 1/10 is not in the returned frequencies. To be there, there must be an integer number k such that k/N = 1/10.
That means N = 10 * k, so N must be a multiple of 10, the period of the sin.
If N is not a multiple of the period of the sin, the sin frequency is not in the fft output.
""")

s = dc.generate_sin(sample_rate=1, amp=1, freq=0.1, phase=0.0, duration=11.0, start=0.0)
f = np.fft.rfftfreq(len(s))
logging.info("rfftfreq(11)=%r", np.fft.rfftfreq(11))
f_amp = np.abs(np.fft.rfft(s))
plt.plot(f, f_amp, 'r+')
plt.show()

logging.info("""
Example 4: N = 15, f = 1/10 => More comparable spikes
Probably N = k*1.5T is the worse choice.
""")

s = dc.generate_sin(sample_rate=1, amp=1, freq=0.1, phase=0.0, duration=15.0, start=0.0)
f = np.fft.rfftfreq(len(s))
f_amp = np.abs(np.fft.rfft(s))
plt.plot(f, f_amp, 'r+')
plt.show()

logging.info("""
Example 5: N = 10005, f = 1/10 => A better spike centered on 0.1
Increasing N helps keeping the error on smaller and smaller regions around f
with N = 100*T + T/2, the spike is concentrated in a 0.01 window, with f(0.1) = about 100*f(0.1+0.01)
with N=10*T, the window is about 0.1 (ten times bigger). It looks like that if you want a 1/100 ratio between the max
outside and inside the window, the window size is 1 / number of periods included = T/N.
""")

s = dc.generate_sin(sample_rate=1, amp=1, freq=0.1, phase=0.0, duration=10005.0, start=0.0)
f = np.fft.rfftfreq(len(s))
f_amp = np.abs(np.fft.rfft(s))
plt.plot(f, f_amp, 'r+')
plt.show()


logging.info("""
Example 6: sampling at 44100 a 50Hz wave over 50.5 periods, around 55 Hz you have 1/10 of the peak at 50Hz,
at 58 (next semitone) about 1/7 of the peak.
""")

s = dc.generate_sin(sample_rate=44100, amp=1, freq=50.0, phase=0.0, duration=1.0 + (0.5/50.0), start=0.0)
f = 44100.0 * np.fft.rfftfreq(len(s))
f_amp = np.abs(np.fft.rfft(s))
plt.plot(f, f_amp, 'r+')
plt.gca().set_xlim(45, 55)
plt.show()

logging.info("""
Example 7: increasing the resolution by 0 padding makes things worse, by creating fake peaks.
""")

s = dc.generate_sin(sample_rate=44100, amp=1, freq=50.0, phase=0.0, duration=1.0 + (0.5/50.0), start=0.0)
f = 44100.0 * np.fft.rfftfreq(10 * len(s))
f_amp = np.abs(np.fft.rfft(s, 10*len(s)))
plt.plot(f, f_amp, 'r+')
plt.gca().set_xlim(45, 55)
plt.show()


logging.info("""
Example 8: sum of 6 sin
if no padding is used it is possible to recognize the peak as local maxima of the function
using padding makes it impossible
""")

freqs = [50.0 * 2.0**(float(i)/12.0) for i in range(1, 7)]
s = sum([dc.generate_sin(sample_rate=44100, amp=1, freq=f, phase=0.0, duration=1.0, start=0.0) for f in freqs])
f = 44100.0 * np.fft.rfftfreq(len(s))
f_amp = np.abs(np.fft.rfft(s, len(s)))
plt.plot(f, f_amp, 'r+')
plt.gca().set_xlim(25, 110)
plt.show()

#
# s = dc.generate_sin(sample_rate, 0.5, 100.0, 0.0, 1.0) + \
#     dc.generate_sin(sample_rate, 0.4, 105.0, 0.0, 1.0) + \
#     dc.generate_sin(sample_rate, 0.4, 93.2, 0.0, 1.0) + \
#     dc.generate_sin(sample_rate, 0.4, 88.039825, 0.0, 1.0)
#
# plt.plot(s)
# plt.plot(s, 'r+')
# plt.show()
#
# min_perc_len = 0.5
# s_mean_offset = int(min_perc_len*len(s))
# s_mean = -np.abs(np.cumsum(s))
# s_mean = s_mean[s_mean_offset:]
#
# # plt.plot(s_mean)
# # plt.plot(s_mean, 'r+')
# # plt.show()
# # periodic_points, _ = find_peaks(s_mean)
# # logger.info("found %d periodic points", len(periodic_points))
# # logger.debug("periodic points: %r", [float(p) / float(sample_rate) for p in periodic_points])
#
# logging.info("fft with estimated periodic point")
# fft_size = s_mean_offset + np.argmax(s_mean)
# idx_to_freq = float(sample_rate) * np.fft.fftfreq(fft_size)
# spectrum_amp = np.abs(np.fft.fft(s, fft_size))
# logger.info("spectrum computed on %d samples, fft size = %d", len(s), len(spectrum_amp))
# logger.info(sorted(-spectrum_amp)[0:16])
#
# plt.plot(idx_to_freq, spectrum_amp)
# plt.plot(idx_to_freq, spectrum_amp, 'r+')
# plt.gca().set_xlim(75, 125)
# plt.show()
#
#
# fft_size = int(sample_rate / fft_resolution_hz)
# idx_to_freq = float(sample_rate) * np.fft.fftfreq(fft_size)
# spectrum_amp = np.abs(np.fft.fft(s, fft_size))
# logger.info("spectrum computed on %d samples, fft size = %d", len(s), len(spectrum_amp))
# logger.info(sorted(-spectrum_amp)[0:16])
#
# plt.plot(idx_to_freq, spectrum_amp)
# plt.plot(idx_to_freq, spectrum_amp, 'r+')
# plt.gca().set_xlim(75, 125)
# plt.show()