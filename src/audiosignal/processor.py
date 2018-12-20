# Floyd Rose Tuner
# Copyright (C) 2018  Daniele Rigato
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
import math
from .signal import Signal
from .generator import sin_wave


LOWER_AUDIBLE_FREQUENCY_HZ = 25
HIGHER_AUDIBLE_FREQUENCY_HZ = 20000
LOWER_SIX_STR_GUITAR_OPEN_STRING_FREQUENCY_HZ = 80
HIGHER_SIX_STR_GUITAR_OPEN_STRING_FREQUENCY_HZ = 330


class SignalProcessor(object):

    def __init__(self,
                 sample_rate,
                 lower_freq=LOWER_AUDIBLE_FREQUENCY_HZ,
                 higher_freq=HIGHER_AUDIBLE_FREQUENCY_HZ,
                 min_window_periods=2):
        self.sample_rate = sample_rate
        self.lower_freq = lower_freq
        self.higher_freq = higher_freq
        self.min_period_length = int(math.floor(sample_rate / higher_freq))
        self.max_period_length = int(math.ceil(sample_rate / lower_freq))
        self.half_window_size = int(min_window_periods * self.max_period_length)
        self.window_size = 2 * self.half_window_size + 1
        self.base_sin = [None] * (self.max_period_length - self.min_period_length)
        self.base_cos = [None] * (self.max_period_length - self.min_period_length)
        self._prepare_base_sin()

    def power(self, signal):
        logging.info("computing power with window_size={} for {} samples, expected iterations "
                     "{}".format(self.window_size, len(signal.samples), self.window_size * len(signal.samples)))
        if not signal.sample_rate == self.sample_rate:
            raise ValueError("Expected signal sample rate = {}, found {}".format(self.sample_rate, signal.sample_rate))
        if not len(signal.samples) >= self.window_size:
            raise ValueError("Expected signal length > {} for this win_size, "
                             "found {}".format(2 * self.half_window_size + 1, len(signal.samples)))
        square_samples = [s**2 for s in signal.samples]
        logging.info("square computed")
        power = [0] * len(signal.samples)
        for i in range(self.half_window_size, len(signal.samples)-self.half_window_size):
            power[i] = sum(square_samples[i - self.half_window_size:i + self.half_window_size + 1]) / self.window_size
        logging.info("sum computed")
        for i in range(0, self.half_window_size):
            power[i] = power[self.half_window_size]
        for i in range(len(signal.samples) - self.half_window_size, len(signal.samples)):
            power[i] = power[len(signal.samples) - self.half_window_size - 1]
        return Signal(sample_rate=signal.sample_rate, samples=power)

    def fast_power(self, signal, resolution_sec):
        step = int(self.sample_rate * resolution_sec)
        logging.info("computing power with window_size={} for {} samples, expected iterations {}"
                     "".format(self.window_size, len(signal.samples), self.window_size * len(signal.samples) / step))
        if not signal.sample_rate == self.sample_rate:
            raise ValueError("Expected signal sample rate = {}, found {}".format(self.sample_rate, signal.sample_rate))
        if not len(signal.samples) >= self.window_size:
            raise ValueError("Expected signal length > {} for this win_size, "
                             "found {}".format(2 * self.half_window_size + 1, len(signal.samples)))
        square_samples = [s**2 for s in signal.samples]
        logging.info("square computed")
        power = []
        for i in range(0, len(signal.samples), step):
            power_value = sum(square_samples[i:i + self.window_size]) / self.window_size
            power.extend([power_value] * step)
        power = power[0:len(signal.samples)]
        return Signal(sample_rate=signal.sample_rate, samples=power)

    def _prepare_base_sin(self):
        logging.info("[starting] prepare base sin for %d functions", self.max_period_length - self.min_period_length)
        for freq_id in range(0, self.max_period_length - self.min_period_length):
            period_len = freq_id + self.min_period_length
            freq_hz = self.sample_rate / period_len
            self.base_sin[freq_id] = sin_wave(1.0, freq_hz, 0.0, self.sample_rate)
            self.base_cos[freq_id] = sin_wave(1.0, freq_hz, math.pi/2, self.sample_rate)
        logging.info("[done] prepare base sin for %d functions", self.max_period_length - self.min_period_length)

    def to_freq_domain(self, signal, freq_step=1):
        freq_amplitude = [0.0] * (self.max_period_length - self.min_period_length)
        freq_phase = [0.0] * (self.max_period_length - self.min_period_length)
        for freq_id in range(0, self.max_period_length - self.min_period_length, freq_step):
            sin_proj = self.correlation_with_periodic_signal(signal, self.base_sin[freq_id])
            cos_proj = self.correlation_with_periodic_signal(signal, self.base_cos[freq_id])
            freq_amplitude[freq_id] = math.sqrt(sin_proj ** 2 + cos_proj ** 2)
            freq_phase[freq_id] = math.atan2(sin_proj, cos_proj) / math.pi
        amp = Signal(self.sample_rate, freq_amplitude)
        phase = Signal(self.sample_rate, freq_phase)
        return amp, phase

    def energetic_frequencies(self, freq_signal, k=0.99):
        max_amp = max(freq_signal.samples)
        threshold = k * max_amp
        max_freq_ids = [i for i in range(len(freq_signal.samples)) if freq_signal.samples[i] > k * threshold]
        return [self.sample_rate / (freq_id + self.min_period_length) for freq_id in max_freq_ids]

    def correlation_with_periodic_signal(self, signal, periodic_signal):
        return sum(self.product_with_periodic_signal(signal, periodic_signal)) / len(signal.samples)

    def product_with_periodic_signal(self, signal, periodic_signal):
        lps = len(periodic_signal.samples)
        return [signal.samples[i] * periodic_signal.samples[i % lps] for i in range(len(signal.samples))]

    # def to_freq_domain(self, signal):
    #     freq_amplitude = [0] * (self.max_period_length - self.min_period_length)
    #     for freq_id in range(0, self.max_period_length - self.min_period_length):
    #         freq_amplitude[freq_id] = self.correlation_with_periodic_base(signal, self.base_sin[freq_id],
    #                                                                       self.base_cos[freq_id])
    #     return Signal(self.sample_rate, freq_amplitude)
    #
    # def correlation_with_periodic_base(self, signal, base1, base2):
    #     proj1 = self.product_with_periodic_signal(signal, base1)
    #     proj2 = self.product_with_periodic_signal(signal, base2)
    #     return sum([math.sqrt(proj1[i]**2 + proj2[i]**2) for i in range(len(signal.samples))]) / len(signal.samples)


def open_string_guitar_signal_processor(sample_rate):
    return SignalProcessor(sample_rate,
                           lower_freq=LOWER_SIX_STR_GUITAR_OPEN_STRING_FREQUENCY_HZ,
                           higher_freq=HIGHER_SIX_STR_GUITAR_OPEN_STRING_FREQUENCY_HZ)
