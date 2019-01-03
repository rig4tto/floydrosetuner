# Floyd Rose Tuner
# Copyright (C) 2019  Daniele Rigato
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

logger = logging.getLogger(__name__)


class SingleSourceApplication(object):
    def __init__(self, audio_source, update_output, **_kvargs):
        self.audio_source = audio_source
        self.update_output = update_output
        self.iteration = 0
        self.current_sample = 0
        self.t =0

    def run(self):
        with self.audio_source:
            self._init()
            logger.info("Starting application")
            while not self.audio_source.eos():
                self.run_once()
        logger.info("Application completed after %d iterations", self.iteration)

    def run_once(self):
        signals = {
            "iteration": self.iteration,
            "current_sample": self.current_sample,
            "t": self.t,
        }
        signals.update(self.audio_source.read())
        samples_read = len(signals["source_signal"])
        self._run_once(signals)
        self.update_output(**signals)
        self.iteration += 1
        self.current_sample += samples_read
        self.t = self.current_sample * self.audio_source.get_sample_rate()
        return signals

    def _init(self):
        raise Exception("_init should be overridden")

    def _run_once(self, signals):
        raise Exception("_run_once should be overridden")
