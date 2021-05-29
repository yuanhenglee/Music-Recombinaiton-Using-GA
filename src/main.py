from Preprocess import ProcessedMIDI
from Individual import Individual
import MusicSegmentation_2 
# from ILBDM import ILBDM
# from RepeatingPattern import findRepeatingPattern
# from SimilarityMatrix import similarityMatrix
# from MusicSegmentation import musicSegmentation
# from MusicSegmentation_2 import musicSegmentation2

from pathlib import Path
from mido import MidiFile

import sys


if __name__ == "__main__":

    try:
        path = sys.argv[1]
    except:
        print("Missing input MIDI file!")

    mid = MidiFile(path)

    parsedMIDI = ProcessedMIDI(mid)

    signaturePossibilities =  MusicSegmentation_2.extractSignatures( parsedMIDI )

    newIndividuals = [Individual(parsedMIDI, parsedMIDI, signature ) for signature in signaturePossibilities ]


    # result_ILBDM = ILBDM(parsedMIDI)

    # result_SM = similarityMatrix(parsedMIDI)

    # musicSegmentation(parsedMIDI, result_SM, result_ILBDM)
    # musicSegmentation2(parsedMIDI, result_ILBDM)
