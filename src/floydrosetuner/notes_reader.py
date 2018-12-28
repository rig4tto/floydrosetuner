import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter, find_peaks


class NotesReader(object):
    def __init__(self, sample_rate, min_freq, max_freq):
        self.min_freq = min_freq
        self.max_freq = max_freq
        self.sample_rate = sample_rate
        self.nyq = 0.5 * sample_rate
        b, a = butter(3, [min_freq / self.nyq, max_freq / self.nyq], btype='band')
        roots_abs_value = np.abs(np.roots(a))
        if not np.all(roots_abs_value < 1):
            raise ValueError("The filter is unstable having roots: %r. Decrease the order or change the parameters",
                             roots_abs_value)
        self.pre_processing_band_filter = (b, a)

    @staticmethod
    def load_wav(filename, min_freq, max_freq):
        sample_rate, audio_signal = wavfile.read(filename)
        notes_reader = NotesReader(sample_rate, min_freq, max_freq)
        return audio_signal, notes_reader

    def read_from_silence_separated_sequence(self, audio_signal):
        pre_processed_signal = self._pre_process(audio_signal)
        power_signal, power_signal_min, power_signal_max = self.compute_power_signal(pre_processed_signal)
        silence_threshold = power_signal_min + 0.1 * (power_signal_max - power_signal_min)
        signal_parts_idx = self.find_sound_parts(power_signal, silence_threshold)
        signal_parts = [pre_processed_signal[p[0]:p[1]] for p in signal_parts_idx]
        main_tones = []
        overtones = []
        spectrums = []
        for signal_part in signal_parts:
            l = len(signal_part)
            trimmed_part = signal_part[int(l/4):int(l*3/4)]
            main_tone, overtones_list, spectrum, idx_to_freq = self.find_main_tone(trimmed_part)
            main_tones.append(main_tone)
            overtones.append(overtones_list)
            spectrums.append((idx_to_freq, spectrum))
        return main_tones, overtones, spectrums

    def _pre_process(self, audio_signal):
        clean_signal = lfilter(self.pre_processing_band_filter[0], self.pre_processing_band_filter[1], audio_signal)
        return clean_signal

    def compute_avg_power(self, audio_signal):
        return np.sqrt(np.average(np.square(audio_signal)))

    def compute_power_signal(self, audio_signal, power_mem_sec = 0.1):
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
        main_tone = idx_to_freq[peaks[0]]
        overtones = [idx_to_freq[p] for p in peaks[1:]]
        return main_tone, overtones, spectrum, idx_to_freq
