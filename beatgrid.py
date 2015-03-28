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
        self._active = set()

        self.width = self.winfo_width()

        self.canvas = tk.Canvas(self, width=600, height=100,
                                background='black')
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.pack(side=tk.TOP, fill="both", expand=1)

        self.scrollbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.scrollbar.config(command=self.canvas.xview)

        self._cb_click = None

    def on_click(self, callback):
        self._cb_click = callback

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
            self._square_to_coord[sq] = (len(self._rows), i)
            row.append(sq)
        self._rows.append(row)

    def _on_click(self, event):
        # map click to square in grid
        x = self.canvas.find_withtag(tk.CURRENT)
        if not isinstance(x, tuple):
            return
        if x[0] not in self._square_to_coord:
            return
        square = x[0]

        # toggle square state
        coords = self._square_to_coord.get(square)
        if coords in self._active:
            self.canvas.itemconfig(square, fill='white')
            self._active.remove(coords)
            if self._cb_click is not None:
                self._cb_click(coords[0], coords[1], False)
        else:
            self.canvas.itemconfig(square, fill='red')
            self._active.add(coords)
            if self._cb_click is not None:
                self._cb_click(coords[0], coords[1], True)

    def get_state(self):
        state = []
        for row in range(len(self._rows)):
            state.append([])
            for col in range(self._bars * self._resolution):
                state[-1].append((row, col) in self._active)
        return state
