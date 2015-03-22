#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bisect

import Tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class AudioSelector(tk.Frame):
    """Visualizes audio signal with selection.

    Arrow keys, space key and enter key can be used to create marks
    and selections.
    """

    def __init__(self, parent, signal, fps, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        self.grid()

        # embed matplotlib gizmos
        figure = Figure((10,2), dpi=100, tight_layout=True)
        canvas = FigureCanvasTkAgg(figure, self)
        canvas.show()
        canvas.get_tk_widget().config(borderwidth=0)
        canvas.get_tk_widget().grid(row=0, column=0,  sticky='NSEW')

        # two plots, no ticks
        top = figure.add_subplot(211)
        top.get_xaxis().set_ticks([])
        top.get_yaxis().set_ticks([])
        bot = figure.add_subplot(212)
        bot.get_xaxis().set_ticks([])
        bot.get_yaxis().set_ticks([])

        # plot spectrogram and raw signal
        timex = [x/float(fps) for x in range(len(signal))]
        top.specgram(signal, Fs=fps)
        bot.plot(timex, signal, c='black')

        # register for mouse and keyboard events
        canvas.mpl_connect("button_press_event", self._onclick)
        canvas.mpl_connect("key_press_event", self._onkey)

        # create the cursor vline
        self.cursor = bot.axvline(0, c='red', alpha=0.6)

        self.top = top
        self.bot = bot
        self.figure = figure

        self._current_selection = None
        self._selections = []
        self._cb_selection = []
        self._marks = []
        self._cb_mark = []

    def on_create_mark(self, callback):
        """Register callback for mark creation events."""

        self._cb_mark.append(callback)

    def on_create_selection(self, callback):
        """Register callback for selection creation events."""

        self._cb_selection.append(callback)

    def delete_mark(self, i):
        """Removes the i:th mark."""

        if i < 0 or i >= len(self._marks):
            raise IndexError("index out of range")
        x, line = self._marks.pop(i)
        line.remove()
        self.figure.canvas.draw()

    def delete_selection(self, i):
        """Removes the i:th selection."""

        if i < 0 or i >= len(self._selections):
            raise IndexError("index out of range")
        start, end, polygon = self._selections.pop(i)
        polygon.remove()
        self.figure.canvas.draw()

    def get_marks(self):
        """Retrieves all marks."""

        return [x for x,_ in self._marks]

    def get_selections(self):
        """Retrieves all selections."""

        return [(start, end) for start, end, _ in self._selections]

    def _onkey(self, event):
        move = {'right': 0.001,
                'up': 0.01,
                'left': -0.001,
                'down': -0.01}
        act = {'ctrl+ ': self._create_mark,
               'enter': self._create_mark,
               ' ': self._toggle_selection,
               'escape': self._cancel_selection}

        if event.key in move:
            self._set_cursor(self._get_cursor() + move[event.key])
        elif event.key in act:
            act[event.key]()
        else:
            print repr(event.key)

    def _onclick(self, event):
        self._set_cursor(event.xdata)

    def _get_cursor(self):
        return self.cursor.get_xdata()[0]

    def _toggle_selection(self):
        if not self._current_selection:
            x = self._get_cursor()
            polygon = self.bot.axvspan(x, x, lw=0, alpha=0.3)
            self._current_selection = (x, x, polygon)
            return

        start, end, polygon = self._current_selection
        self._current_selection = None
        start, end = min(start, end), max(start, end)

        new = True
        remove = set()
        for i in range(len(self._selections)):
            s, e, p = self._selections[i]
            if s <= start <= e and s <= end <= e:
                new = False
                break
            if s <= start <= e:
                remove.add(i)
                start = s
            if s <= end <= e:
                remove.add(i)
                end = e

        for i in sorted(remove, reverse=True):
            self.delete_selection(i)

        if new:
            polygon.set_xy([[start, 0.0], [start, 1.0], [end, 1.0], [end, 0.0]])
            self._selections.append((start, end, polygon))
        self.figure.canvas.draw()

    def _cancel_selection(self):
        if self._current_selection:
            _,__, polygon = self._current_selection
            self._current_selection = None
            polygon.remove()
            self.figure.canvas.draw()

    def _set_cursor(self, x):
        x = max(0, min(x, self.bot.get_xbound()[1]))
        self.cursor.set_xdata([x, x])

        if self._current_selection:
            start, end, polygon = self._current_selection
            polygon.set_xy([[start, 0.0], [start, 1.0], [x, 1.0], [x, 0.0]])
            self._current_selection = (start, x, polygon)

        self.figure.canvas.draw()

    def _create_mark(self):
        x = self._get_cursor()

        # draw mark on rad signal
        line = self.bot.axvline(x, c='blue', alpha=0.7)
        self.figure.canvas.draw()

        # record
        bisect.bisect(self._marks, (x, line))
        i = bisect.bisect(self._marks, (x, line))
        self._marks.insert(i, (x, line))

        # call back
        marks = [x for x, line in self._marks]
        for cb in self._cb_mark:
            cb(i, marks)

