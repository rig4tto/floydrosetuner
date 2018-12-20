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


class Signal(object):
    """
    Represent an audio signal as a discrete sequence of sample taken at a given rate
    """

    def __init__(self, sample_rate: int, samples: list):
        assert sample_rate is not None, "sample_rate can not be None"
        assert isinstance(sample_rate, int), "sample_rate must be an int, instead was {} of type {}".format(
            sample_rate, type(sample_rate))
        if not sample_rate > 0:
            raise ValueError("sample_rate must be greater than 0")
        assert samples is not None, "samples can not be None"
        assert isinstance(samples, list), \
            "samples must be a list, instead was {} of type {}".format(samples, type(samples))
        assert not [type(sample) for sample in samples if not isinstance(sample, float)], \
            "all samples must be float, found {}".format(set([type(sample)
                                                              for sample in samples
                                                              if not isinstance(sample, float)]))

        out_of_range_samples = [sample for sample in samples if not -1.0 <= sample <= 1.0]
        if out_of_range_samples:
            logging.error("Expected a normalized signal, found invalid samples: %r", out_of_range_samples)
            raise ValueError("Expected a normalized signal, found samples not in [-1.0; 1.0]")

        self.sample_rate = sample_rate
        self.samples = samples
