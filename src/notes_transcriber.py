import logging
import numpy as np

from floydrosetuner.audio_stream import AudioStream
from floydrosetuner.notes_reader import NotesReader
from floydrosetuner.pitch import Pitch

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


BUFFER_SECONDS_FOR_ANALYSIS = 1.0
MIN_AMP = 0.05
MIN_NUMBER_OF_ANALYSIS = 10
MAX_DIFF_HZ = 1

with AudioStream(buffer_sec=BUFFER_SECONDS_FOR_ANALYSIS) as audio_stream:
    notes_reader = NotesReader(sample_rate=audio_stream.sample_rate, min_freq=30.0, max_freq=2000.0)
    min_pow = notes_reader.power_for_amp(MIN_AMP)
    logger.info("waiting for signal with amp > %r, i.e. power > %r", MIN_AMP, min_pow)

    iteration = 0
    detected_pitches = []
    last_overtones = None
    while True:
        indata = audio_stream.read()
        audio_stream.write(indata)

        audio_signal = audio_stream.buffer
        audio_signal = notes_reader.pre_process(audio_signal)
        avg_pow = notes_reader.compute_avg_power(audio_signal)
        logger.debug("power %r", avg_pow)
        if avg_pow > min_pow:
            main_tone, overtones, spectrum, idx_to_freq = notes_reader.find_main_tone(audio_signal)
            last_overtones = overtones
            pitch = Pitch(main_tone)
            if not detected_pitches:
                logger.debug("detected sound, probably %r", pitch)
            detected_pitches.append(pitch)
            logger.debug("power %r found pitch %r", avg_pow, pitch)
        elif detected_pitches:
            l = len(detected_pitches)
            if l > MIN_NUMBER_OF_ANALYSIS:
                detected_pitches = detected_pitches[int(l/3):int(l*2/3)]
                frequencies = [p.frequency for p in detected_pitches]
                max_diff = max(frequencies) - min(frequencies)
                freq_mean = np.mean(frequencies)
                p = Pitch(freq_mean)
                if max_diff <= MAX_DIFF_HZ:
                    logger.info("detected pitch %r %r (max diff %r over %d analysis)",
                                 p.frequency, p, max_diff, len(detected_pitches))
                    logger.info("overtones: %r", [Pitch(o) for o in overtones if o > 0])
                else:
                    logger.info("discarded pitch %r %r (max diff %r over %d analysis)",
                                 p.frequency, p, max_diff, len(detected_pitches))
            detected_pitches = []
        else:
            # silence, nothing to do
            pass
        iteration += 1
