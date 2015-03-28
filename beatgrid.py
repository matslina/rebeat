# -*- coding: utf-8 -*-

import Tkinter as tk

PX_PER_SQUARE = 15
DEFAULT_ROWS = 16


class UIRow:
    COLOR_ON = 'red'
    COLOR_OFF = 'white'

    def __init__(self, canvas, rowi, columns=16):
        # columns must be power of 2
        assert columns & (columns - 1) == 0

        self.canvas = canvas
        self.rowi = rowi

        self.squares = []
        for _ in range(columns):
            self._append_square()

        self._cb_toggle = None

    def set_state(self, state):
        assert len(state) == len(self.squares)

        for active, square in zip(state, self.squares):
            color = self.COLOR_ON if active else self.COLOR_OFF
            self.canvas.itemconfig(square, fill=color)

    def on_toggle(self, callback):
        self._cb_toggle = callback

    def _append_square(self):
        bbox = self._square_bbox(len(self.squares))
        sq = self.canvas.create_rectangle(*bbox,
                                          fill=self.COLOR_OFF)
        self.canvas.tag_bind(sq, '<Button-1>', self._square_click)
        self.squares.append(sq)

    def _square_click(self, event):
        # figure out which column click was in
        x = self.canvas.find_withtag(tk.CURRENT)
        if not isinstance(x, tuple):
            return
        try:
            column = self.squares.index(x[0])
        except ValueError:
            return

        if self._cb_toggle is not None:
            self._cb_toggle(self.rowi, column)

    def _square_bbox(self, x):
        y = self.rowi
        return (x * (1 + PX_PER_SQUARE) + 2,
                y * (1 + PX_PER_SQUARE) + 2,
                x * (1 + PX_PER_SQUARE) + 2 + PX_PER_SQUARE,
                y * (1 + PX_PER_SQUARE) + 2 + PX_PER_SQUARE)


class BeatGrid(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # A canvas on which we draw rows
        self.canvas = tk.Canvas(self, width=600, height=100,
                                background='black')
        self.canvas.pack(side=tk.TOP)

        # UIRow instances in _rows, actual state in _state
        self._rows = []
        self._state = []

        self._bars = 4
        self._resolution = 4

    def _toggle(self, row, col):
        self._state[row][col] = not self._state[row][col]
        self._rows[row].set_state(self._state[row])

    def add_row(self, position=-1):
        if position < 0:
            position = len(self._rows)

        row = UIRow(self.canvas, len(self._rows), 16)
        row.on_toggle(self._toggle)
        self._rows.append(row)
        self._state.insert(position, [False] * 16)

        for i in range(position, len(self._rows)):
            self._rows[i].set_state(self._state[i])

    def get_state(self):
        return self._state
