"""Represents a pitch, e.g. a musical tone whose only relevant attribute is the frequency.

https://en.wikipedia.org/wiki/Musical_tone
https://en.wikipedia.org/wiki/Pitch_(music)
"""


#: Mapping from standard note name to the semitone starting from C=0
NOTE_TO_SEMITONE = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "B": 11,
}

#: Minimum valid frequency, no pitch can have a frequency lower than this
MIN_FREQUENCY = 0

#: Maximum valid frequency, no pitch can have a frequency greater than this
MAX_FREQUENCY = 20000


class Pitch(object):
    """Represents a pitch, e.g. a musical tone whose only relevant attribute is the frequency.
    """

    def __init__(self, frequency):
        """
        :param frequency: frequency measured in hertz
        :type frequency: float
        :rtype Pitch
        """
        if frequency < MIN_FREQUENCY or frequency > MAX_FREQUENCY:
            raise ValueError("invalid frequency {} valid range[{}, {}]".format(frequency, MIN_FREQUENCY, MAX_FREQUENCY))
        self.frequency = frequency

    @staticmethod
    def parse(str):
        semitone = NOTE_TO_SEMITONE[str[0]]
        return Pitch(440.0*pow(2.0,(semitone-9.0)/12.0))
