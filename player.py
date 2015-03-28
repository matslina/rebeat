
class Player:

    def __init__(self, filename):
        raise NotImplementedError()

    def play(self, start, stop, duration=None, stretch=[]):
        """Plays a section of the file.

        The section from 'start' until 'stop' seconds into the sample
        is played. If 'duration' is given, then the sample is
        stretched to span exactly 'duration' seconds.

        If 'stretch' is provided, then the 2-tuple in 'stretch' marks
        stretchable regions in the section.
        """
        raise NotImplementedError()

    def get_signal(self):
        """Returns the audio signal as a list of floats in (-1.0, 1.0)."""
        raise NotImplementedError()

    def get_length(self):
        """Returns length of sample in seconds."""
        raise NotImplementedError()

