# -*- coding: utf-8 -*-

import Tkinter as tk

PX_PER_SQUARE = 15
DEFAULT_ROWS = 16
DEFAULT_COLUMNS = 4

class BeatGrid(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self._rows = []
        self._bars = 4
        self._resolution = 4
        self._square_to_coord = {}

        self.width = self.winfo_width()

        self.canvas = tk.Canvas(self, width=600, height=100,
                                background='black')
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.pack(side=tk.TOP, fill="both", expand=1)

        self.scrollbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.scrollbar.config(command=self.canvas.xview)

        self.add_row()
        self.add_row()
        self.add_row()
        self.add_row()

    def on_click(self, callback):
        raise NotImplementedError()

    def on_rowselect(self, callback):
        raise NotImplementedError()

    def _square_bbox(self, x, y):
        return (x * (1 + PX_PER_SQUARE) + 2,
                y * (1 + PX_PER_SQUARE) + 2,
                x * (1 + PX_PER_SQUARE) + 2 + PX_PER_SQUARE,
                y * (1 + PX_PER_SQUARE) + 2 + PX_PER_SQUARE)

    def add_row(self, title=None):
        row = []
        for i in range(self._bars * self._resolution):
            bbox = self._square_bbox(i, len(self._rows))
            sq = self.canvas.create_rectangle(*bbox,
                                              fill='white')
            print "registering", sq, "as", (len(self._rows), i)
            self._square_to_coord[sq] = (len(self._rows), i)
            row.append(sq)

    def _on_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        square = tuple(map(int, self.canvas.find_closest(x, y)))[0]
        print "click", x,y, "i.e.", square, "i.e.", self._square_to_coord.get(square)

    def fill(self):
        return
        self.update_idletasks()
