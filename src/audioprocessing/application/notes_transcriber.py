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
from audioprocessing.processor.pitch_tracker import PitchTracker
from audioprocessing.processor.note_tracker import NoteTracker
from audioprocessing.processor.buffer import Buffer


logger = logging.getLogger(__name__)


def update_console_output(notes, **other_signals):
    if len(notes) > 0:
        logger.info(notes)


class NotesTranscriber(SingleSourceApplication):
    def __init__(self, audio_source, update_output=update_console_output, monophonic=False, **kvargs):
        super().__init__(audio_source, update_output, **kvargs)
        self.monophonic = monophonic

    def _init(self):
        self.spectrum_analyzer = SpectrumAnalyzer(self.audio_source.get_sample_rate())
        self.pitch_tracker = PitchTracker()
        self.buffer = Buffer(self.audio_source.get_sample_rate(), buffer_duration=20.0)
        self.note_tracker = NoteTracker()

    def _run_once(self, signals):
        signals.update(self.buffer.process(**signals))
        signals.update(self.spectrum_analyzer.process(**signals))
        if self.monophonic:
            signals["pitches"] = signals["pitches"][0:1]
        signals.update(self.pitch_tracker.process(**signals))
        signals.update(self.note_tracker.process(**signals))


if __name__ == '__main__':
    from audioprocessing.io.sound_card import SoundCard
    logging.basicConfig(level=logging.INFO)
    audio_source = SoundCard(processing_rate=8.0)
    NotesTranscriber(audio_source).run()
