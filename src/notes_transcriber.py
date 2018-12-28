import logging
import numpy as np

from floydrosetuner.audio_stream import AudioStream
from floydrosetuner.notes_reader import NotesReader
from floydrosetuner.pitch import Pitch

logging.basicConfig(level=logging.INFO)

MIN_POW = 0.006
MIN_NUMBER_OF_ANALYSIS = 10
MAX_DIFF_HZ = 1


with AudioStream() as audio_stream:
    notes_reader = NotesReader(sample_rate=audio_stream.sample_rate, min_freq=30.0, max_freq=2000.0)
    iteration = 0
    detected_pitches = []
    while True:
        indata = audio_stream.read()
        audio_stream.write(indata)

        audio_signal = audio_stream.buffer
        avg_pow = notes_reader.compute_avg_power(audio_signal)
        logging.debug("power %r", avg_pow)
        if avg_pow > MIN_POW:
            main_tone, overtones, spectrum, idx_to_freq = notes_reader.find_main_tone(audio_signal)
            pitch = Pitch(main_tone)
            if not detected_pitches:
                logging.debug("detected sound, probably %r", pitch)
            detected_pitches.append(pitch)
            logging.debug("power %r found pitch %r", avg_pow, pitch)
        elif detected_pitches:
            l = len(detected_pitches)
            if l > MIN_NUMBER_OF_ANALYSIS:
                detected_pitches = detected_pitches[int(l/3):int(l*2/3)]
                frequencies = [p.frequency for p in detected_pitches]
                max_diff = max(frequencies) - min(frequencies)
                freq_mean = np.mean(frequencies)
                p = Pitch(freq_mean)
                if max_diff <= MAX_DIFF_HZ:
                    logging.info("detected pitch %r %r (max diff %r over %d analysis)",
                                 p.frequency, p, max_diff, len(detected_pitches))
                else:
                    logging.info("discarded pitch %r %r (max diff %r over %d analysis)",
                                 p.frequency, p, max_diff, len(detected_pitches))
            detected_pitches = []
        else:
            # silence, nothing to do
            pass
        iteration += 1
