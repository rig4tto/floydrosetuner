import unittest
import logging
from floydrosetuner.notes_reader import NotesReader
from floydrosetuner.pitch import Pitch
import matplotlib.pyplot as plt

from tst_utils import path_for_audio_sample


logging.basicConfig(level=logging.INFO)
DETAILED_DEBUG_ENABLED = False


class NotesReaderTest(unittest.TestCase):
    def test_integ_with_wav(self):
        filename = "cmaj_scale_32bit_pcm_float.wav"
        expected_pitches = Pitch.parse_all("C4 D4 E4 F4 G4 A4 B4 C5")
        max_error_herz = 2.0
        audio_signal, notes_reader = NotesReader.load_wav(path_for_audio_sample(filename), 50.0, 800.0)
        main_tones, overtones, spectrums = notes_reader.read_from_silence_separated_sequence(audio_signal)
        main_pitches = [Pitch(f) for f in main_tones]
        nparts = len(main_tones)
        logging.info("found %d parts", nparts)
        if DETAILED_DEBUG_ENABLED:
            for i in range(nparts):
                logging.info("part %d has main tone %r (%r), overtones %r",
                             i, main_pitches[i], main_tones[i], overtones[i])
                plt.subplot(nparts, 1, i+1)
                plt.plot(spectrums[i][0], spectrums[i][1])
                plt.title("Part {} spectrum".format(i))
                plt.grid()
            plt.show()
        for i in range(nparts):
            logging.info("part %d has main tone %r (f=%r)", i, main_pitches[i], main_tones[i])
            self.assertEqual(expected_pitches[i].note, main_pitches[i].note)
            self.assertEqual(expected_pitches[i].octave, main_pitches[i].octave)
            self.assertLess(main_pitches[i].error, max_error_herz)

