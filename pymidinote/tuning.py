import math, csv, re

def check_negative(freq):
    if freq < 0:
        raise ValueError("negative frequency")

def cent_diff(freq1, freq2):
    """Returns the difference between 2 frequencies in cents

    Parameters
    ----------
    freq1 : float
        The first frequency
    freq2 : float
        The second frequency

    Returns
    -------
    float 
        The difference between the 2 frequencies
    """
    return 1200*math.log2(freq2/freq1)
	
def detune(freq, cents=0):
    """Detunes the desired frequency using cents

    Parameters
    ----------
    freq : float
        The frequency
    cents : float
        The amount to detune in cents (accepts negative values)

    Returns
    -------
    float 
        The detuned frequency
    """
    check_negative(freq)
    return freq*2**(cents/1200)
	
def overtones(freq, n=16):
    """Returns the overtones of the desired frequency

    Parameters
    ----------
    freq : float
        The frequency
    n : int
        The number of overtones to generate

    Returns
    -------
    list
        A list containing the frequency's overtones in ascending order 
        (the base frequency is included as the first element)
    """
    check_negative(freq)
    return [freq*i for i in range(1,n + 1)]

def mirror(freq, freq_axis):
    """Returns the flipped frequency around the freq axis

    Parameters
    ----------
    freq : float
        The frequency to flip
    freq_axis : float
        The the frequency to use as axis of the mirror

    Returns
    -------
    float
        The mirrored frequency
    """
    check_negative(freq)
    return freq_axis**2/freq

def ifreq(freq_axis, index, steps=12):
    """Returns a frequency using step and octave index

    Parameters
    ----------
    freq_axis : float
        The frequency acting as the 'axis'
    index : tuple
        A 2-element tuple describing the distance of the desired frequency
        from freq, where the first element is the number of steps and the 
        second is the number of octaves (accepts negative values)
    steps : int
        The number of equal steps to divide the octave (default is 12)

    Returns
    -------
    float
        a frequency based on EDO distance from freq
    """
    check_negative(freq_axis)
    return freq_axis*2**(index[0]/steps + index[1])

def get_closest_midi_note(freq, cent_thresh):
    """Iterates the midi dict to find the item with smallest frequency difference,
    determined by the cent threshold.

    Parameters
    ----------
    freq : float
        The given frequency
    cent_thresh : float
        The cent threshold

    Returns
    -------
        The midi note nearest to the given frequency
    """
    for item in midi_dict.items():
        if abs(cent_diff(freq, item[1])) <= cent_thresh:
            return item

def get_midi(freq):
    """Returns a MIDI event representing the given frequency.
    Microtonal frequencies will be slotted to the nearest MIDI note
    with a pitch wheel value applied to it.

    Parameters
    ----------
    freq : float
        The desired frequency 

    Returns
    -------
        A tuple consisting of the nearest MIDI note and pitch wheel value
        (will be 0 if frequency is in Equal Temperament)
    """
    max_wheel = 8191
    max_cents = 200
    ratio = max_wheel/max_cents
    midi_num, midi_freq = get_closest_midi_note(freq, 50.1)
    wheel = int(cent_diff(midi_freq, freq)*ratio)
    return midi_num, wheel


class EDO:
    """Equal Divisions of Octave; produces 'Notes' using step/octave indexing.
    """

    def __init__(self, A4, steps=0, table=None, start=0):
        """Constructs an EDO either using steps or a table 
        (size of table determines total steps)

        Parameters
        ----------
        A4 : float
            Concert pitch that is represented as A4 in western music
        steps : int
            Total steps to split octave into
        table : list
            A list of lists containing the different names for each note
        start : int
            The index of A4 in the table.
        """
        self.A4 = A4
        self.start = start
        if table is not None:
            size = len(table)
            # move elements according to where the start is
            if start != 0:
                self.table = table[:start] + table[start:]
            else:
                self.table = table
            self.dict = {n:i for i in range(size) for n in self.table[i]}
            self.steps = size
        elif steps != 0:
            self.table = None
            self.steps = steps
        else:
            raise ValueError('either table or steps must be specified')

    def __getitem__(self, index):
        # extract note name and octave if string
        if isinstance(index, str):
            if self.dict is None:
                raise Exception('no dictionary defined in EDO')
            split = re.findall(r"[A-Z][b#]?|\d", index)
            # i : step index
            i = self.dict[split[0]]
            # j : octave index
            j = int(split[1])
            index = i, j
        # nothing to do when tuple, just check if it isn't
        elif not isinstance(index, tuple):
            raise ValueError('invalid index type')
        return Note(self, index)
            
    def step_in_cents(self):
        return cent_diff(self[0,4].freq(), self[1,4].freq())

    def __str__(self):
        return '<{}.{} steps={} A4={} at {}>'.format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.steps,
            self.A4,
            hex(id(self)))
        
    def __repr__(self):
        return str(self)

    @staticmethod
    def twelve(A4=440):
        """Returns 12 EDO
        """
        return EDO(A4, table=table, start=9)

class Note:
    """Class representing notes. Can produce more notes using
     the EDO used or using intervals.
    """

    def __init__(self, edo, index):
        self.edo = edo
        self.index = index
        self.start = 0
        self.end = 0
        self.velocity = 96
        self.cents = 0

    def names(self):
        if self.edo is None or self.edo.table is None:
            return []
        return self.edo.table[self.index[0]]

    def name(self):
        if self.edo is None or self.edo.table is None:
            return ''
        return self.names()[0]

    def A4(self):
        return self.edo.A4

    def detune(self, cents):
        self.cents = cents
        return self

    def freq(self):
        A4 = self.edo.A4
        i = self.index[0] - self.edo.steps - self.edo.start
        j = self.index[1] - 3

        return detune(ifreq(A4, (i, j), self.edo.steps), self.cents)

    def __getitem__(self, index):
        """Creates a new note based on index. The EDO and detuned cents are also passed.
        Index: can be either int or tuple. int specifies 
        the steps from this note according to the EDO, tuple
        also provides the octave.
        Interval: by using float. Sets this note as the axis for the new note.
        """
        if isinstance(index, (int, tuple)):
            if isinstance(index, tuple):
                i = self.index[0] + index[0]
                j = self.index[1] + index[1]
            else:
                i = self.index[0] + index
                j = self.index[1]
            n_index = i%self.edo.steps, i//self.edo.steps + j
            cents = 0
        elif isinstance(index, float):
            freq = self.freq()
            cent_dist = cent_diff(freq, freq * index)
            step_in_cents = self.edo.step_in_cents()
            closest_i = round(round(cent_dist/step_in_cents))
            i = self.index[0] + closest_i
            j = self.index[1]
            n_index = i%self.edo.steps, i//self.edo.steps + j
            cents = cent_dist - closest_i*step_in_cents
        else:
            raise ValueError('invalid value for index/interval')
        return Note(self.edo, n_index).detune(self.cents + cents)

    def get_midi(self):
        return get_midi(self.freq())

    def __str__(self):
        return '<{}.{} name(s)={}, index={}, ({}c) at {}>'.format(
        self.__class__.__module__,
        self.__class__.__name__,
        self.names(),
        self.index,
        round(self.cents, 2),
        hex(id(self)))
        
    def __repr__(self):
        return str(self)

import pathlib

filename = pathlib.Path(__file__).parent / '12edo.csv'
table = list(csv.reader(open(filename)))
midi_dict =  {i : ifreq(440, (i -69, 0)) for i in range(128)}
