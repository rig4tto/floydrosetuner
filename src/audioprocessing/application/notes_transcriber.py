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
from audioprocessing.application.application import SingleSourceApplication
from audioprocessing.processor.spectrum_analyzer import SpectrumAnalyzer
from audioprocessing.model.pitch import Pitch


logger = logging.getLogger(__name__)


def update_console_output(spectrum_peaks_freq, pitches, **other_signals):
    if len(pitches) > 0:
        logger.info("peaks: %r", pitches)


class NotesTranscriber(SingleSourceApplication):
    def __init__(self, audio_source, update_output=update_console_output, **kvargs):
        super().__init__(audio_source, update_output, **kvargs)

    def _init(self):
        self.spectrum_analyzer = SpectrumAnalyzer(self.audio_source.get_sample_rate())

    def _run_once(self, signals):
        signals.update(self.spectrum_analyzer.process(**signals))
        signals["pitches"] = [Pitch(p) for p in signals["spectrum_peaks_freq"]]


if __name__ == '__main__':
    from audioprocessing.io.sound_card import SoundCard
    logging.basicConfig(level=logging.INFO)
    audio_source = SoundCard()
    NotesTranscriber(audio_source).run()
