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

import unittest
import logging

from tst_utils import path_for_audio_sample

from audioprocessing.application.notes_transcriber import NotesTranscriber
from audioprocessing.io.synthesizer import GeneratedSoundReader, create_melody_generator, ZERO_TIMBRE
from audioprocessing.io.wav_file import WavFileReader
from audioprocessing.model.pitch import Pitch

logging.basicConfig(level=logging.INFO)

SAMPLE_RATE = 44100
PROCESSING_RATE = 8.0
BEAT = 120.0


class NoteTranscriberTest(unittest.TestCase):

    def test_app_with_generated_note(self):
        melody = "C"
        melody_generator = create_melody_generator(melody, timbre=ZERO_TIMBRE, fade_in=0.0, fade_out=0.0)
        audio_source = GeneratedSoundReader(SAMPLE_RATE, PROCESSING_RATE, BEAT, melody_generator)
        output_pitches = set([])

        def collect_output(pitches, **_other_signals):
            output_pitches.update(pitches)
            logging.info("pitches: %r", pitches)
        NotesTranscriber(audio_source, update_output=collect_output).run()
        self.assertEqual(set([Pitch.parse("C4")]), output_pitches)

    def test_app_with_wav(self):
        audio_source = WavFileReader(filename=path_for_audio_sample("cmaj_scale_32bit_pcm_float.wav"))
        output_pitches = []

        def collect_output(pitches, **_other_signals):
            output_pitches.extend(pitches)
            logging.info("pitches: %r", pitches)
        NotesTranscriber(audio_source, update_output=collect_output).run()
