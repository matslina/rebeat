#! /usr/bin/env python

from multiprocessing import Process, Queue

import struct
import wave

BLOCKSIZE = 16384


class Player:
    def __init__(self, filename):

        self.readaudio(filename)

    def readaudio(self, filename):
        w = wave.open(filename)
        assert w.getsampwidth() == 2
        self.raw = w.readframes(w.getnframes())
        self.frames = [struct.unpack("<h", self.raw[i:i+2])[0] / float(2**15)
                       for i in range(0, len(self.raw), 2)]
        self.fps = w.getframerate()*2
        print "read %s, %i frames, %i SPS, %f seconds " % (
            filename, len(self.frames), self.fps*2, len(self.frames)/self.fps)

    def play(self, start, stop, duration=None, stretch=[]):
        """Plays a section of the file.

        The section from 'start' until 'stop' seconds into the sample
        is played. If 'duration' is given, then the sample is
        stretched to span exactly 'duration' seconds.

        If 'stretch' is provided, then the 2-tuple in 'stretch' marks
        stretchable regions in the section.
        """

        starto = int(start * self.fps * 2)
        endo = int(stop * self.fps * 2)

        print "playing from %i to %i" % (starto, endo)

        if duration:
            # do stretch stuff here
            print "stretching not implmented yet, suckah"
        else:
            playbuf = self.raw[starto:endo]

        self.q = Queue()
        p = Process(target=self.audiowriter, args=(self.fps, self.q,))
        p.start()

        self.q.put(['play', playbuf])

    def abort_playback(self):
        """Abort a previously requested playback.

        Playback actually ends after the last BLOCKSIZE has been written.
        """
        self.q.put(['abort'])

    def audiowriter(self, fps, q):
        import pyaudio
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(2),
                        channels=2,
                        rate=fps/2,
                        output=True)

        while True:
            pack = q.get()

            if pack[0] == 'play':
                playbuf = [pack[1]]
                playbufoff = 0
                off = [0]
                while off[playbufoff] < len(playbuf[playbufoff]):
                    stream.write(
                        playbuf[playbufoff][off[playbufoff]:off[playbufoff] +
                                            BLOCKSIZE])
                    if not q.empty():
                        newpack = q.get(False)
                        if newpack:
                            if newpack[0] == 'play':
                                playbuf.append(newpack[1])
                                off.append(0)
                            elif newpack[0] == 'abort':
                                break
                    off[playbufoff] += BLOCKSIZE
                    if (off[playbufoff] < len(playbuf[playbufoff])
                            and len(playbuf) > playbufoff+1):
                        playbufoff = playbufoff + 1

            else:
                print "command %s not implemented/valid" % pack[0]

        stream.stop_stream()
        stream.close()

    def get_signal(self):
        """Returns the audio signal as a list of floats in (-1.0, 1.0)."""
        return self.frames

    def get_length(self):
        """Returns length of sample in seconds."""
        return len(self.frames)/self.fps
