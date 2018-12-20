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

import wave
import logging
from .signal import Signal


def dump_signal(signal, file_path):
    with open(file_path, "w") as fout:
        fout.writelines([str(signal.sample_rate) + '\n'])
        fout.writelines([str(sample) + '\n' for sample in signal.samples])
    logging.info("written %d samples to %s", len(signal.samples), file_path)


def load_signal(file_path):
    with open(file_path, "r") as fin:
        sample_rate = int(fin.readline())
        samples = [float(line) for line in fin.readlines()]
    logging.info("loaded %d samples from %s", len(samples), file_path)
    return Signal(sample_rate=sample_rate, samples=samples)


def load_wav(file_path):
    """
    Load a wav file returning a signal

    The wav file must have only one channel (mono) and be encoded as signed pcm.
    Sample width and frame rate can be arbitrary, this function will deal with them

    :param file_path: path to the wav file
    :return: a signal with the content of the wav file
    """
    with wave.open(file_path, "rb") as f:
        len_in_seconds = f.getnframes() / (f.getframerate() * f.getnchannels())
        logging.info("loading wave file %s (framerate: %d, channels: %d, frames: %d, seconds %s, sample width %d)",
                     file_path, f.getframerate(), f.getnchannels(), f.getnframes(),
                     len_in_seconds, f.getsampwidth())
        if not f.getnchannels() == 1:
            raise ValueError("only 1 channel wave files are supported")  # TODO: support multiple channel wave files
        frames = f.readframes(f.getnframes())
        samples = [frame_to_float(frames, i, f.getsampwidth()) for i in range(0, f.getnframes())]
        return Signal(sample_rate=f.getframerate(), samples=samples)


def frame_to_float(frames, pos, sampwidth):
    """
    Converts a frame (an array of bytes) to a float value between [-1, 1] representing a sample

    The frame is expected to start with the less significant byte, so for instance [1,0,0] corresponds to 1

    :param frames: the array of bytes representing the frames having size sampwidth * n_frames
    :param pos: the position, i.e. the index of the frame to be converted [0;n_frames]
    :param sampwidth: the size of a frame
    :return: a float value representing the sample in position pos
    """
    max_module = 128 * 256 ** (sampwidth - 1)
    unsigned_value = sum([frames[pos*sampwidth + i] * 256 ** i for i in range(0, sampwidth)])
    signed_value = unsigned_to_signed_int(unsigned_value, sampwidth)
    normalized_value = signed_value / max_module
    return normalized_value


def unsigned_to_signed_int(value, n_bytes):
    """
    Fix signed integers that have been parsed from a byte array like unsigned ones.

    Given the number of bytes of the integer, it is possible to compute the value for min_signed_int=b10...0
    Values smaller than min_signed_int are already correct, numbers greater than min_signed_int must be fixed
    complementing them

    For instance, for 1 byte
    10000000 = 128 is min_signed_int, must be complemented to -128
    01111111 = 127 is the greatest value lower than min_signed_int
    11111111 = 255 is -1 obtained as the difference between 111111111 == 256 == 2*min_signed_int and its unsigned value

    :param value: unsigned value to convert
    :param n_bytes: size of the integer
    :return: the signed value
    """
    min_signed_int_value = 128 * 256 ** (n_bytes - 1)
    if value >= min_signed_int_value:
        value = - (2 * min_signed_int_value - value)
    return value
