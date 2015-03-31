#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bisect

import Tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class SelectionController:

    def __init__(self, range_min, range_max):
        self._min = range_min
        self._max = range_max

        self._selections = []
        self._partitions = []
        self._cb_partition_created = None
        self._cb_selection_created = None

    def on_partition_created(self, callback):
        self._cb_partition_created = callback

    def on_selection_created(self, callback):
        self._cb_selection_created = callback

    def get_selections(self):
        return self._selections

    def get_partitions(self):
        return self._partitions

    def remove_selection(self, i):
        self._selection.pop(i)

    def remove_partition(self, i):
        self._partitions.pop(i)

    def create_partition(self, where):
        if where < self._min or where > self._max:
            raise ValueError("partition point out of range")

        i = bisect.bisect(self._partitions, where)
        self._partitions.insert(i, where)

        if self._cb_partition_created:
            self._cb_partition_created(i)

        return i

    def create_selection(self, from_, to):
        from_ = min(from_, to)
        to = max(from_, to)

        if from_ < self._min or to > self._max:
            raise ValueError("selection out of range")

        remove = []

        for i, (s, e) in enumerate(self._selections):
            # new selection completely contained
            if s <= from_ and to <= e:
                return

            # old selection completely contained
            if from_ <= s and e <= to:
                remove.append(i)

            # new selection overlaps
            elif s <= from_ <= e or s <= to <= e:
                from_, to = min(from_, s), max(to, e)
                remove.append(i)

        for i in sorted(remove, reverse=True):
            self._selections.pop(i)

        # insert so that list remains ordered
        pos = bisect.bisect(self._partitions, (from_, to))
        self._selections.insert(pos, (from_, to))

        if self._cb_selection_created:
            self._cb_selection_created(i)

        return pos


class AudioSelector(tk.Frame):
    """Visualizes audio signal with selection.

    Arrow keys, space key and enter key can be used to create marks
    and selections.
    """

    def __init__(self, parent, signal, fps, controller, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        self._selections = controller
        self.grid()

        # embed matplotlib gizmos
        figure = Figure((10,2), dpi=100, tight_layout=True, facecolor='white')
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
        self._polygons = []
        self._lines = []

    def _onkey(self, event):
        move = {'right': 0.001,
                'up': 0.01,
                'left': -0.001,
                'down': -0.01}
        act = {'ctrl+ ': self._create_mark,
               'enter': self._create_mark,
               ' ': self._selection_toggle,
               'escape': self._selection_cancel}

        if event.key in move:
            self._set_cursor(self._get_cursor() + move[event.key])
        elif event.key in act:
            act[event.key]()
        else:
            print repr(event.key)

    def _onclick(self, event):
        self._set_cursor(event.xdata)

    def _selection_toggle(self):
        if not self._current_selection:
            self._selection_start()
        else:
            self._selection_stop()

    def _selection_start(self):
        x = self._get_cursor()
        polygon = self.bot.axvspan(x, x, lw=0, alpha=0.3)
        self._current_selection = (x, x, polygon)

    def _selection_update(self, x):
        start, end, polygon = self._current_selection
        polygon.set_xy([[start, 0.0], [start, 1.0], [x, 1.0], [x, 0.0]])
        self._current_selection = (start, x, polygon)

    def _selection_cancel(self):
        _,__, polygon = self._current_selection
        polygon.remove()
        self.figure.canvas.draw()
        self._current_selection = None

    def _selection_stop(self):
        start, end, polygon = self._current_selection
        self._selections.create_selection(start, end)
        self._polygons.append(polygon)
        self._current_selection = None
        self._redraw()

    def _redraw(self):
        sels = self._selections.get_selections()
        parts = self._selections.get_partitions()

        # hide dead matplotlib "patches"
        for patch in self._polygons[len(sels):] + self._lines[len(parts):]:
            patch.visible(False)

        # create as many new ones as needed
        self._polygons += [self.bot.axvspan([0, 0], [0, 0], lw=0, alpha=0.3)
                           for _ in range(len(sels) - len(self._polygons))]
        self._lines += [self.bot.axvline(0, c='blue', alpha=0.7)
                        for _ in range(len(parts) - len(self._lines))]

        # place them where they should be at
        for poly, sel in zip(self._polygons, sels):
            poly.set_xy([sel[0], 0.0], [sel[0], 1.0],
                        [sel[1], 1.0], [sel[1], 0.0])
        for line, part in zip(self._lines, parts):
            line.set_xdata([part, part])

        self.figure.canvas.draw()

    def _get_cursor(self):
        return self.cursor.get_xdata()[0]

    def _set_cursor(self, x):
        x = max(0, min(x, self.bot.get_xbound()[1]))
        self.cursor.set_xdata([x, x])
        if self._current_selection:
            self._selection_update(x)
        self.figure.canvas.draw()

    def _create_mark(self):
        self._selections.create_partition(self._get_cursor())
        self._redraw()
