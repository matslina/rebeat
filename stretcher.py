# -*- coding: utf-8 -*-

import ctypes


class Stretcher:

    def __init__(self, data, nchannels, samplerate, samplewidth):
        self._l = ctypes.cdll.LoadLibrary('./stretcher.so')
        self._s = self._l.stretcher_new(data, len(data), nchannels,
                                        samplerate, samplewidth)

        self._l.stretcher_length.restype = ctypes.c_int
        self._l.stretcher_data.restype = ctypes.c_void_p

    def stretch(self, duration):
        self._l.stretcher_stretch(self._s, ctypes.c_float(duration))
        print "done stretching!"
        n = self._l.stretcher_length(self._s)
        print "got %d bytes" % n
        d = self._l.stretcher_data(self._s)
        print "data at", repr(d)
        return ctypes.string_at(d, n)



if __name__ == "__main__":
    import wave
    import pyaudio
    import sys

    w = wave.open(sys.argv[1])
    samplewidth = w.getsampwidth()
    nchannels = w.getnchannels()
    fps = w.getframerate()
    data = w.readframes(w.getnframes())

    samplerate = fps * nchannels

    st = Stretcher(data, nchannels, samplerate, samplewidth)

    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(2),
                    channels=nchannels,
                    rate=fps,
                    output=True)
    import time
    start = time.time()
    stream.start_stream()
    stream.write(st.stretch(float(sys.argv[2])))
    stream.stop_stream()
    print float(len(data)) / (samplewidth * samplerate)
    print time.time() - start
