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
import numpy as np
from audioprocessing.application.application import SingleSourceApplication
from audioprocessing.processor.buffer import Buffer
import sys
import time
from audioprocessing.io.wav_file import WavFileReader
from audioprocessing.io.sound_card import SoundCard
from audioprocessing.model.pitch import FREQ_C0

if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk


logger = logging.getLogger(__name__)


def interleave(a, b):
    c = np.empty((a.size + b.size,), dtype=a.dtype)
    c[0::2] = a
    c[1::2] = b
    return c


class DefaultPlayerApplication(SingleSourceApplication):
    def __init__(self, audio_source, update_output, **kvargs):
        super().__init__(audio_source, update_output, **kvargs)

    def _init(self):
        self.buffer = Buffer(self.audio_source.get_sample_rate(), buffer_duration=1.0)
        self.spectrum_freq = self.audio_source.get_sample_rate() * np.fft.rfftfreq(self.buffer.buffer_len)
        self.spectrum_semitones_from_c0 = np.log2(self.spectrum_freq / FREQ_C0) * 12.0

    def _run_once(self, signals):
        signals.update(self.buffer.process(**signals))
        spectrum = np.abs(np.fft.rfft(signals["buffered_signal"]))

        signals.update({
            "spectrum": spectrum,
            "spectrum_freq": self.spectrum_freq,
            "spectrum_semitones_from_c0": self.spectrum_semitones_from_c0
        })


OCTAVE_COLORS = ["#000", "#f00", "#ff0", "#0f0", "#0ff", "#00f", "#f0f", "#0ff", "#fff"]
NOTE_COLORS = ["#f00", "#fff", "#ff0", "#fff", "#0f0", "#0ff", "#fff", "#00f", "#fff", "#f0f", "#fff", "#000"]


class Player(tk.Frame):
    def __init__(self, audio_source, application_cls=DefaultPlayerApplication, master=None):
        self.audio_source = audio_source
        self.application = application_cls(audio_source, update_output=self.update_ui)
        self.sound_card = None
        tk.Frame.__init__(self, master)
        self.start_time = time.time()
        self.nit = 0
        self.grid()
        self.createWidgets()

        self.audio_source.__enter__()
        self.application._init()
        self.run_multiple()

    def getCW(self):
        return 1200

    def getCH(self):
        return 700

    def semitonesToCx(self, semitones):
        return ((semitones + 0.5) % 12) * self.getCW() / 12.0

    def createWidgets(self):
        self.eps_val = tk.StringVar()
        self.eps_label = tk.Label(self, font=('Helvetica', 24))
        self.eps_label.pack(side="top")
        self.eps_label["textvariable"] = self.eps_val
        self.canvas = tk.Canvas(self, width=self.getCW(), height=self.getCH())
        self.canvas.pack()
        self.quitButton = tk.Button(self, text='Quit', command=self.quit)
        self.quitButton.pack(side="bottom")

    def run_multiple(self):
        self.run_once()
        self.after(10, self.run_multiple)

    def run_once(self):
        if not self.audio_source.eos():
            self.application.run_once()

    def update_ui(self, source_signal, spectrum_semitones_from_c0, spectrum, **other_signals):
        if not self.sound_card:
            self.sound_card = SoundCard(sample_rate=audio_source.get_sample_rate(), processing_rate=10.0)
            self.sound_card.__enter__()
        self.sound_card.write(source_signal)

        cur_time = time.time()
        exec_time = cur_time - self.start_time
        eps = float(self.nit) / exec_time
        self.eps_val.set("fps={}".format(round(eps, 1)))
        self.nit += 1

        self.canvas.delete("all")

        x = spectrum_semitones_from_c0
        y = spectrum
        # mask = np.mod(np.arange(x.size), 20) == 0
        # x = x[mask]
        # y = y[mask]

        for i in range(12):
            lx = self.semitonesToCx(i)
            self.canvas.create_line(lx, 0, lx, self.getCH(), fill=NOTE_COLORS[i], width=2)

        for i in range(3, 6):
            mask = (x >= i*12.0 - 0.5) & (x < i*12.0 + 12.0 - 0.5)
            x1 = x[mask]
            y1 = y[mask]
            cx = self.semitonesToCx(x1)
            cy = self.getCH() - 20 - y1 * 400.0 / 100.0
            pts = interleave(cx, cy).astype(int)
            self.canvas.create_line([p for p in pts], fill=OCTAVE_COLORS[i], width=3)




if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    audio_source = WavFileReader(filename="C:/data/audio_samples/lazy_frog.wav", processing_rate=1.0)
    root = tk.Tk()
    player = Player(audio_source, master=root)
    player.mainloop()
