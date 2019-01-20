import time
import logging
import numpy as np
import sys

if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk


logging.basicConfig(level=logging.INFO)


def interleave(a, b):
    c = np.empty((a.size + b.size,), dtype=a.dtype)
    c[0::2] = a
    c[1::2] = b
    return c


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.start_time = time.time()
        self.nit = 0
        self.grid()
        self.createWidgets()

    def createWidgets(self):
        self.eps_val = tk.StringVar()
        self.eps_label = tk.Label(self, font=('Helvetica', 24))
        self.eps_label.pack(side="top")
        self.eps_label["textvariable"] = self.eps_val

        self.canvas = tk.Canvas(self, width=500, height=500)
        self.canvas.pack()

        self.quitButton = tk.Button(self, text='Quit', command=self.quit)
        self.quitButton.pack(side="bottom")
        self.run_multiple()

    def run_multiple(self):
        self.run_once()
        self.after(10, self.run_multiple)

    def run_once(self):
        cur_time = time.time()
        exec_time = cur_time - self.start_time
        eps = float(self.nit) / exec_time
        self.eps_val.set("fps={}".format(round(eps, 1)))
        self.nit += 1
        logging.debug("execution %r eps %r", self.nit, eps)

        self.canvas.delete("all")

        x = np.linspace(0, 1.0, 100000)
        y = np.sin(2 * np.pi * 1.0 * (x + exec_time))
        cx = x * 400.0 / 1.0 + 50
        cy = (y+1) * 400.0 / 2.0 + 50
        pts = interleave(cx, cy).astype(int)
        self.canvas.create_line([p for p in pts])


root = tk.Tk()
app = Application(master=root)
app.master.title('Sample application')
app.mainloop()
