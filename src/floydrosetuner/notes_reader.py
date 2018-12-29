import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter, find_peaks
import logging

logger = logging.getLogger(__name__)

DEFAULT_MIN_FREQ = 60.0
DEFAULT_MAX_FREQ = 2000.0


class NotesReader(object):
    def __init__(self, sample_rate, min_freq=DEFAULT_MIN_FREQ, max_freq=DEFAULT_MAX_FREQ):
        self.min_freq = min_freq
        self.max_freq = max_freq
        self.sample_rate = sample_rate
        self.nyq = 0.5 * sample_rate
        self.pre_processing_band_filter = self.create_band_filter(min_freq, max_freq)

    @staticmethod
    def load_wav(filename, min_freq, max_freq):
        sample_rate, audio_signal = wavfile.read(filename)
        notes_reader = NotesReader(sample_rate, min_freq, max_freq)
        return audio_signal, notes_reader

    def read_from_silence_separated_sequence(self, audio_signal, main_tone_assumption=True):
        pre_processed_signal = self.pre_process(audio_signal)
        power_signal, power_signal_min, power_signal_max = self.compute_power_signal(pre_processed_signal)
        silence_threshold = power_signal_min + 0.1 * (power_signal_max - power_signal_min)
        signal_parts_idx = self.find_sound_parts(power_signal, silence_threshold)
        signal_parts = [pre_processed_signal[p[0]:p[1]] for p in signal_parts_idx]
        main_tones = []
        overtones = []
        spectrums = []
        for signal_part in signal_parts:
            l = len(signal_part)
            trimmed_part = signal_part[int(l/10):int(l*9/10)]
            main_tone, overtones_list, spectrum, idx_to_freq = self.find_main_tone(trimmed_part)
            main_tones.append(main_tone)
            overtones.append(overtones_list)
            spectrums.append((idx_to_freq, spectrum))
        return main_tones, overtones, spectrums

    def pre_process(self, audio_signal):
        clean_signal = NotesReader.apply_band_filter(self.pre_processing_band_filter, audio_signal, 3)
        return clean_signal

    def compute_avg_power(self, audio_signal):
        return np.sqrt(np.average(np.square(audio_signal)))

    def compute_power_signal(self, audio_signal, power_mem_sec=0.1):
        power_signal = np.square(audio_signal)
        power_signal_smooth = np.zeros(len(power_signal))
        win_size = int(power_mem_sec * self.sample_rate)
        cur_sum = sum(power_signal[0:win_size])
        for i in range(win_size, len(power_signal)):
            cur_sum += power_signal[i]
            cur_sum -= power_signal[i - win_size]
            power_signal_smooth[i] = cur_sum / float(win_size)
        power_signal = power_signal_smooth
        power_signal_min = np.min(power_signal)
        power_signal_max = np.max(power_signal)
        return power_signal, power_signal_min, power_signal_max

    def find_sound_parts(self, power_signal, silence_threshold):
        parts = []
        cursor = 0
        while cursor < len(power_signal):
            while cursor < len(power_signal) and power_signal[cursor] < silence_threshold:
                cursor += 1
            first_noise_pos = cursor
            while cursor < len(power_signal) and power_signal[cursor] > silence_threshold:
                cursor += 1
            if first_noise_pos < len(power_signal):
                parts.append((first_noise_pos, cursor))
        return parts

    def find_main_tone(self, audio_signal):
        spectrum = np.abs(np.fft.fft(audio_signal))
        idx_to_freq = float(self.sample_rate) * np.fft.fftfreq(len(spectrum))
        spectrum_max = spectrum[np.argmax(spectrum)]
        min_peaks_height = spectrum_max * 0.3
        peaks, _ = find_peaks(spectrum, min_peaks_height)
        overtones = [idx_to_freq[p] for p in peaks[1:]]

        main_tone_id = peaks[0]
        main_tone = idx_to_freq[main_tone_id]
        max_err = abs(main_tone - idx_to_freq[main_tone_id + 1]) if main_tone_id + 1 < len(idx_to_freq) else 0
        max_err = max(max_err, abs(main_tone - idx_to_freq[main_tone_id - 1]) if main_tone_id - 1 > 0 else 0)

        main_tone, _ = self.refine_main_tone(audio_signal, main_tone, err_abs=max_err, err_perc=0.0)
        return main_tone, overtones, spectrum, idx_to_freq

    def refine_main_tone(self, audio_signal, main_tone, err_abs=2.0, err_perc=0.1, min_cross=4):
        band = err_abs + err_perc * main_tone
        band_filter = self.create_band_filter(main_tone - band, main_tone + band)
        audio_signal = NotesReader.apply_band_filter(band_filter, audio_signal, 3)
        audio_signal_clean = NotesReader.normalize(audio_signal)
        main_tone_assuming_clean_sin, n_cross = self.find_clean_sin_freq(audio_signal_clean, tr=0.7)
        if n_cross > min_cross:
            if abs(main_tone_assuming_clean_sin - main_tone) < band:
                logger.info("optimization: fourier main tone: %r replaced by clean sin main tone: %r with %r cross",
                             main_tone, main_tone_assuming_clean_sin, n_cross)
                return main_tone_assuming_clean_sin, True
            else:
                logger.warning("fourier main tone (%r) is not consistent with clean sin main tone(%r) with %r cross",
                                main_tone, main_tone_assuming_clean_sin, n_cross)
        else:
            logger.warning("too few cross to optimize the main tone %r < %r", n_cross, min_cross)
        return main_tone, False

    def create_band_filter(self, min_freq, max_freq):
        b, a = butter(1, [min_freq / self.nyq, max_freq / self.nyq], btype='band')
        roots_abs_value = np.abs(np.roots(a))
        if not np.all(roots_abs_value < 1):
            raise ValueError("The filter is unstable having roots: %r. Decrease the order or change the parameters",
                             roots_abs_value)
        return (b, a)

    @staticmethod
    def apply_band_filter(filter, audio_signal, times=1):
        filtered_signal = lfilter(filter[0], filter[1], audio_signal)
        for i in range(times - 1):
            filtered_signal = lfilter(filter[0], filter[1], filtered_signal)
        return filtered_signal

    @staticmethod
    def normalize(audio_signal):
        # the new signal is between -1 and 1
        amp = np.ptp(audio_signal)
        if amp > 0.000001:
            return (audio_signal - np.min(audio_signal)) * 2.0 / np.ptp(audio_signal) - 1.0
        else:
            logger.warning("normalize does not work with a constant audio signal")
            return audio_signal

    def find_clean_sin_freq(self, audio_signal, tr=None):
        if not tr:
            tr = np.max(audio_signal) * 2.0 / 3.0
        tr_pos = abs(tr)
        tr_neg = -abs(tr)

        state = "0"
        crossing_points = []
        crossing_delta = []
        last_crossing_point = None
        crossing_delta_sum = 0
        n_crossing_delta = 0
        for i in range(len(audio_signal)):
            v = audio_signal[i]
            if v > tr_pos:
                if state == "n":
                    crossing_points.append(i)
                    if last_crossing_point:
                        crossing_delta.append(i - last_crossing_point)
                        crossing_delta_sum += i - last_crossing_point
                        n_crossing_delta += 1
                    last_crossing_point = i
                state = "p"
            elif v < tr_neg:
                state = "n"
        main_tone = None
        if n_crossing_delta > 0:
            main_tone = float(self.sample_rate * n_crossing_delta) / float(crossing_delta_sum)
        return main_tone, n_crossing_delta

    def generate_t(self, duration, start=0.0):
        return start + np.arange(0.0, float(duration * self.sample_rate), dtype=np.float32) / float(self.sample_rate)

    def generate_sin(self, amp, freq, phase, duration, start=0):
        t_signal = self.generate_t(duration=duration, start=start)
        return amp * np.sin(2.0 * np.pi * freq * t_signal + phase)

    def power_for_amp(self, amp):
        return self.compute_avg_power(self.generate_sin(amp, 1.0, 0.0, 1.0))
