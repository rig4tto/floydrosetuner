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
from audioprocessing.processor.harmony_analyzer import HarmonyAnalyzer
from audioprocessing.processor.buffer import Buffer


logger = logging.getLogger(__name__)


def no_output(**other_signals):
    pass


def update_console_output(powerful_semitones, semitone_power, **other_signals):
    logging.debug("%r %r %r", max(semitone_power), min(semitone_power), sorted(semitone_power))
    if len(powerful_semitones):
        logger.info(powerful_semitones)


class SongAnalyzer(SingleSourceApplication):
    def __init__(self, audio_source, update_output=update_console_output, **kvargs):
        super().__init__(audio_source, update_output, **kvargs)

    def _init(self):
        self.buffer = Buffer(self.audio_source.get_sample_rate(), buffer_duration=20.0)
        self.harmony_analyzer = HarmonyAnalyzer(self.audio_source.get_sample_rate())

    def _run_once(self, signals):
        signals.update(self.buffer.process(**signals))
        signals.update(self.harmony_analyzer.process(**signals))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # from audioprocessing.io.sound_card import SoundCard
    # audio_source = SoundCard(processing_rate=10.0)
    # from audioprocessing.io.synthesizer import GeneratedSoundReader, create_melody_generator, ZERO_TIMBRE
    # melody = "C4 D6 E2 B3"
    # melody_generator = create_melody_generator(melody, timbre=ZERO_TIMBRE, fade_in=0.0, fade_out=0.0)
    # audio_source = GeneratedSoundReader(44100, 5, 30, melody_generator)

    from audioprocessing.io.wav_file import WavFileReader
    audio_source = WavFileReader(filename="C:/data/audio_samples/lazy_frog.wav", processing_rate=1.0)

    from audioprocessing.application.notes_transcriber import NotesTranscriber
    NotesTranscriber(audio_source).run()
    #SongAnalyzer(audio_source).run()
