from numpy import sin, linspace, pi,average;
from scipy import fft, arange, ifft
import scipy
import numpy as np
from scipy.optimize import leastsq
from scipy.signal import butter, lfilter, find_peaks
from floydrosetuner.notes_reader import NotesReader

sample_rate = 1000

a0 = 0.6
f0 = 30.4
ph0 = np.pi * 1.0/4.0

Ttot = 1


nsamples = Ttot * sample_rate

t_array = np.arange(0.0, float(nsamples), dtype=np.float32) / float(sample_rate)
print("t", [v for v in t_array])
sin0_array = a0 * np.sin(2.0*np.pi*f0*t_array + ph0)

audio_signal = sin0_array
print("sin", [v for v in audio_signal])

tr = 0.3
tr_pos = abs(tr)
tr_neg = -abs(tr)

state = "0"
crossing_points = []
for i in range(len(audio_signal)):
    v = audio_signal[i]
    if v > tr_pos:
        if state == "n":
            crossing_points.append(i)
        state = "p"
    elif v < tr_neg:
        state = "n"
print("crossing ", crossing_points)

crossing_delta = [float(crossing_points[i+1] - crossing_points[i]) for i in range(len(crossing_points)-1)]
print("crossing delta", crossing_delta)
freq_est = sample_rate / np.mean(crossing_delta)
print("freq est", freq_est)
freq_est = NotesReader(sample_rate=sample_rate, min_freq=10, max_freq=100).find_clean_sin_freq(audio_signal)
print("freq est", freq_est)

spectrum = np.abs(np.fft.fft(audio_signal))
idx_to_freq = float(sample_rate) * np.fft.fftfreq(len(spectrum))
spectrum_max = spectrum[np.argmax(spectrum)]
min_peaks_height = spectrum_max * 0.3
peaks, _ = find_peaks(spectrum, min_peaks_height)
main_tone = idx_to_freq[peaks[0]]

print ("main tone: %r" % main_tone, )