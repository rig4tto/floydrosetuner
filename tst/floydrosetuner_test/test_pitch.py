import unittest

from floydrosetuner.pitch import Pitch, MIN_FREQUENCY, MAX_FREQUENCY


class NoteTest(unittest.TestCase):
    def test_ctor_with_valid_frequncy(self):
        Pitch(440.0)

    def test_ctor_with_invalid_frequency_negative(self):
        with self.assertRaises(ValueError):
            Pitch(-1)

    def test_ctor_with_invalid_frequency_too_low(self):
        with self.assertRaises(ValueError):
            Pitch(MIN_FREQUENCY - 1)

    def test_ctor_with_invalid_frequency_too_high(self):
        with self.assertRaises(ValueError):
            Pitch(MAX_FREQUENCY + 1)

    def test_parse(self):
        self.assertEqual(440.0, Pitch.parse("A").frequency)
