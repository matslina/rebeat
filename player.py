#! /usr/bin/env python

import pyaudio
import multiprocessing
import Queue
import struct
import wave

BLOCKSIZE = 16384


class Player:
    def __init__(self, filename):

        w = wave.open(filename)
        self.samplewidth = w.getsampwidth()
        self.nchannels = w.getnchannels()
        self.frames = w.readframes(w.getnframes())
        self.fps = w.getframerate()

        print "Loaded", filename
        print "Width", self.samplewidth
        print "FPS", self.fps
        print "numframes", len(self.frames)
        print "channels", self.nchannels
        print "duration", len(self.frames) / float(self.samplewidth * self.nchannels * self.fps)

        self.q = multiprocessing.Queue()
        self.p = multiprocessing.Process(target=self._worker)
        self.p.start()

    def _worker(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(2),
                        channels=2,
                        rate=self.fps/2,
                        output=True)

        active = False

        while True:
            try:
                cmd = self.q.get(block=not active)
            except Queue.Empty:
                cmd = None

            if cmd:
                if cmd[0] == 'play':
                    active = True
                    pos = cmd[1]
                    end = cmd[2]
                elif cmd[0] == 'abort':
                    active = False
                elif cmd[0] == 'stop':
                    break

            if active:
                block_start, block_end = pos, min(end, pos + BLOCKSIZE)
                stream.write(self.frames[block_start:block_end])
                pos = block_end
                if pos >= end:
                    active = False

        stream.stop()
        stream.close()

    def play(self, start, stop, duration=None, stretch=[]):
        """Plays a section of the file.

        The section from 'start' until 'stop' seconds into the sample
        is played. If 'duration' is given, then the sample is
        stretched to span exactly 'duration' seconds.

        If 'stretch' is provided, then the 2-tuple in 'stretch' marks
        stretchable regions in the section.
        """

        a = int(start * self.fps) * self.samplewidth * self.nchannels
        b = int(stop * self.fps) * self.samplewidth * self.nchannels

        self.q.put(('play',
                    a, b,
                    duration,
                    stretch))

    def abort_playback(self):
        """Abort a previously requested playback.

        Playback actually ends after the last BLOCKSIZE has been written.
        """
        self.q.put(('abort',))

    def close(self):
        self.q.put(('stop',))

    def get_signal(self):
        """Returns the audio signal as a list of floats in (-1.0, 1.0)."""

        return [struct.unpack("<h", self.frames[i:i+2])[0] / float(2**15)
                for i in range(0, len(self.frames), 2)]

    def get_length(self):
        """Returns length of sample in seconds."""
        return len(self.frames)/self.fps

    def get_fps(self):
        """Returns frames per second."""
        return self.fps

if __name__ == "__main__":
    import sys
    p = Player(sys.argv[1])
    print "Playing"
    p.play(0, p.get_length())
    import time
    time.sleep(5)
    p.close()
    print "Done"
