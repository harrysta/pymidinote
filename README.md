# PyMIDI Note

PyMIDI Note is a Python library for generating, manipulating and arranging abstract MIDI data using exact frequencies and/or different tuning systems.
* Easily get the MIDI equivalent of any frequency in the form of the note and pitchwheel data.
* Create an EDO of any division of your choice and generate notes by providing their index.
* The generated notes are as flexible, since they refer their generator EDO, allowing detuning and note generation with respect to their index.

**Note**: This library does not import/export MIDI files/objects. [Mido](https://github.com/mido/mido) is recommended for that use case.

## Examples

```python
from pymidinote import tuning as tn	

edo = tn.EDO.twelve()
chords = []
# Dmin7
chord1 = [edo['D3'], edo['A3'], edo['C4'], edo['F4']]
# G7
chord2 = [edo['D3'], edo['G3'], edo['B3'], edo['F4']]
# Cmaj7
chord3 = [edo['C3'], edo['G3'], edo['B3'], edo['E4']]

chords = [chord1, chord2, chord3]
```
This is a simple ii-V-I chord progression using the standard 12-tone system. The notes are retrieved by providing the EDO instance a string containing the note name and octave respectively. The note names are only available for the 12-tone system by default. Other tuning system note names can be provided in the form of a csv file in the EDO's constructor. The first chord can also be created using note index:

```python
chord = [edo[2, 3], edo[9, 3], edo[0, 4], edo[5, 4]]
```
The first number refers to the step index (we start from C in 12-EDO) and the second refers to the octave index.
```python
edo = tn.EDO(440, steps=5)
note = edo[3, 4].detune(30)
midi_note = note.get_midi()
```
In the above example we are creating a tuning system that splits the octave into 5 equal divisions, which is called 5-EDO for short. The frequency of the notes from any EDO can be altered using the `detune` function, which detunes the note by the amount of cents provided. The note in the example will therefore be 30 cents sharper than the original (negative numbers will make them flatter). Finally, `get_midi` will return the note in MIDI data form - a tuple containing the MIDI step index and the pitchwheel value respectively.
