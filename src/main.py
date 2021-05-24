from Preprocess import ProcessedMIDI
from ILBDM import ILBDM
from RepeatingPattern import findRepeatingPattern
from SimilarityMatrix import similarityMatrix
from MusicSegmentation import musicSegmentation
from MusicSegmentation_2 import musicSegmentation2

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

    result_ILBDM = ILBDM(period)

    result_SM = similarityMatrix(period)

    musicSegmentation(period, result_SM, result_ILBDM)
    musicSegmentation2(period, result_ILBDM)
