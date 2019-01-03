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

from audioprocessing.model.pitch import Pitch
from audioprocessing.application.application import SingleSourceApplication
from audioprocessing.processor.band_peak_finder import BandPeakFinder
from audioprocessing.processor.buffer import Buffer
from audioprocessing.processor.rms_processor import RmsProcessor
from audioprocessing.processor.sound_splitter import SoundSplitter


logger = logging.getLogger(__name__)

SIX_STRINGS_GUITAR_STANDARD_TUNING = [
    Pitch.parse("E2"),
    Pitch.parse("A2"),
    Pitch.parse("D3"),
    Pitch.parse("G3"),
    Pitch.parse("B3"),
    Pitch.parse("E4"),
]

BAND_SIZE = 1.5

SIX_STRINGS_GUITAR_BANDS = [(p.add_semitones(-BAND_SIZE).frequency, p.add_semitones(BAND_SIZE).frequency)
                            for p in SIX_STRINGS_GUITAR_STANDARD_TUNING]


def update_console_output(split_sound, bands_peak, **other_signals):
    if len(split_sound) > 0:
        if len(bands_peak) > 0 and len([p for p in bands_peak if p is None]) == 0:
            logger.info("found sound of length %r having band picks %r", len(split_sound), bands_peak)
            for i in range(len(bands_peak)):
                expected_pitch = SIX_STRINGS_GUITAR_STANDARD_TUNING[i]
                actual_pitch = Pitch(bands_peak[i])
                error_in_semitones = actual_pitch.offset_from_c0 - expected_pitch.offset_from_c0
                logging.info("String %r - error = %r semitones, found %r", i, error_in_semitones, actual_pitch)
        else:
            logging.warning("Could not detect all the strings")


class NotesTranscriber(SingleSourceApplication):
    def __init__(self, audio_source, update_output=update_console_output, **kvargs):
        super().__init__(audio_source, update_output, **kvargs)

    def _init(self):
        self.rms_processor = RmsProcessor()
        self.sound_splitter = SoundSplitter()
        self.band_peak_finder = BandPeakFinder(self.audio_source.get_sample_rate(), bands=SIX_STRINGS_GUITAR_BANDS)
        self.buffer = Buffer(self.audio_source.get_sample_rate(), buffer_duration=20.0)

    def _run_once(self, signals):
        signals.update(self.buffer.process(**signals))
        signals.update(self.rms_processor.process(**signals))
        signals.update(self.sound_splitter.process(**signals))
        signals.update(self.band_peak_finder.process(**self.remap(signals, {"source_signal": "split_sound"})))


if __name__ == '__main__':
    from audioprocessing.io.sound_card import SoundCard
    logging.basicConfig(level=logging.INFO)
    audio_source = SoundCard(processing_rate=10.0)
    NotesTranscriber(audio_source).run()
