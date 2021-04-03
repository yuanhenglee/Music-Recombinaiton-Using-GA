from Preprocess import ProcessedMIDI
from ILBDM import ILBDM

from pathlib import Path
from mido import MidiFile

import sys


if __name__ == "__main__":

    try:
        path = sys.argv[1]
    except:
        print("Missing input MIDI file!")

    mid = MidiFile(path)

    period = ProcessedMIDI(mid)

    period.printPeriod()

    ILBDM(period)
