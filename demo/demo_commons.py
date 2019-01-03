import logging
import numpy as np

logger = logging.getLogger(__name__)


def normalize(audio_signal):
    # the new signal is between -1 and 1
    amp = np.ptp(audio_signal)
    if amp > 0.000001:
        return (audio_signal - np.min(audio_signal)) * 2.0 / np.ptp(audio_signal) - 1.0
    else:
        logger.warning("normalize does not work with a constant audio signal")
        return audio_signal


def generate_t(sample_rate, duration, start=0.0):
    return start + np.arange(0.0, float(duration) * float(sample_rate), dtype=np.float32) / float(sample_rate)


def generate_sin(sample_rate, amp, freq, phase, duration, start=0.0):
    t_signal = generate_t(sample_rate, duration=duration, start=start)
    s = amp * np.sin(2.0 * np.pi * float(freq) * t_signal + float(phase))
    return s


def generate_fade(sample_rate, duration, fade_in, fade_out):
    fade_in_signal = np.arange(0.0, 1.0, 1.0 / (float(fade_in) * float(sample_rate)), dtype=np.float32)
    fade_out_signal = np.arange(1.0, 0.0, - 1.0 / (float(fade_out) * float(sample_rate)), dtype=np.float32)
    left_over = int(duration * sample_rate) - len(fade_in_signal) - len(fade_out_signal)
    if left_over > 0:
        left_over_signal = np.ones(left_over, dtype=np.float32)
        return np.concatenate([fade_in_signal, left_over_signal, fade_out_signal])
    else:
        raise ValueError("fade is too long")


def generate_note(sample_rate, amp, freq, duration, fade_in=0.01, fade_out=0.01):
    return amp * generate_sin(sample_rate, 1.0, freq, 0.0, duration) * generate_fade(sample_rate, duration, fade_in, fade_out)
