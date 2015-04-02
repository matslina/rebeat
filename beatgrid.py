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
        self.items = []

        # kill square and cross in box 0
        box0 = self._square_bbox(0)
        kill_sq = self.canvas.create_rectangle(*box0, fill='gray')
        kill_c1 = self.canvas.create_line(box0[0], box0[1],
                                          box0[2], box0[3])
        kill_c2 = self.canvas.create_line(box0[2], box0[1],
                                          box0[0], box0[3])
        self.canvas.tag_bind(kill_sq, '<Button-1>', self._kill_click)
        self.canvas.tag_bind(kill_c1, '<Button-1>', self._kill_click)
        self.canvas.tag_bind(kill_c2, '<Button-1>', self._kill_click)
        self.items.extend([box0, kill_sq, kill_c1, kill_c2])

        # play square and triangle in box 1
        box1 = self._square_bbox(1)
        poly = [(box1[0], box1[1]),
                (box1[2] - 2, box1[1] + int(PX_PER_SQUARE / 2.0)),
                (box1[0], box1[3]),
                (box1[0], box1[1])]
        play_sq = self.canvas.create_rectangle(*box1, fill='gray')
        play_tr = self.canvas.create_polygon(poly, fill='white')
        self.canvas.tag_bind(play_sq, '<Button-1>', self._play_click)
        self.canvas.tag_bind(play_tr, '<Button-1>', self._play_click)
        self.items.extend([play_sq, play_tr])

        # toggleable squares in boxes 2 and onwards
        self.squares = []
        for _ in range(columns):
            self._append_square()

        self._cb_toggle = None
        self._cb_play = None
        self._cb_kill = None

    def set_state(self, state):
        assert len(state) == len(self.squares)

        for active, square in zip(state, self.squares):
            color = self.COLOR_ON if active else self.COLOR_OFF
            self.canvas.itemconfig(square, fill=color)

    def on_toggle(self, callback):
        self._cb_toggle = callback

    def on_play(self, callback):
        self._cb_play = callback

    def on_kill(self, callback):
        self._cb_kill = callback

    def remove(self):
        for item in self.items:
            self.canvas.delete(item)

    def _append_square(self):
        bbox = self._square_bbox(3 + len(self.squares))
        sq = self.canvas.create_rectangle(*bbox,
                                          fill=self.COLOR_OFF)
        self.canvas.tag_bind(sq, '<Button-1>', self._square_click)
        self.squares.append(sq)
        self.items.append(sq)

    def _play_click(self, event):
        if self._cb_play is not None:
            self._cb_play(self.rowi)

    def _kill_click(self, event):
        if self._cb_kill is not None:
            self._cb_kill(self.rowi)

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

        self._cb_play = None
        self._cb_kill = None

    def on_play(self, callback):
        self._cb_play = callback

    def on_kill(self, callback):
        self._cb_kill = callback

    def _toggle(self, row, col):
        self._state[row][col] = not self._state[row][col]
        self._rows[row].set_state(self._state[row])

    def _play(self, row):
        if self._cb_play is not None:
            self._cb_play(row)

    def _kill(self, row):
        # first row is start of sample. can't be killed.
        if row == 0:
            return

        if self._cb_kill is not None:
            self._cb_kill(row)
        self._rows[-1].remove()
        self._rows.pop(-1)
        self._state.pop(row)
        for i in range(len(self._rows)):
            self._rows[i].set_state(self._state[i])

    def add_row(self, position=-1):
        if position < 0:
            position = len(self._rows)

        row = UIRow(self.canvas, len(self._rows), 16)
        row.on_toggle(self._toggle)
        row.on_play(self._play)
        row.on_kill(self._kill)
        self._rows.append(row)
        self._state.insert(position, [False] * 16)

        for i in range(position, len(self._rows)):
            self._rows[i].set_state(self._state[i])

    def get_state(self):
        return self._state
