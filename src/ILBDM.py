import copy
import numpy as np
import Constant as C
from Utility import formattedPrint


def ILBDM(target):
    # DEFINE ICR PR DURATION WEIGHT
    ICR = 1
    PR = 1

    seqTable = copy.deepcopy(target.noteSeq)

    def calculateWeight(sequenceIndex):
        sumOfWeight = np.zeros(target.numberOfNotes)
        # ICR + PR + duration
        for i, previous in enumerate(seqTable[sequenceIndex][:-1]):

            current = seqTable[sequenceIndex][i+1]
            PIncrement = 0
            CIncrement = 0
            # calculate accumulative beat weight
            if sequenceIndex == C.ACCUMULATIVEINDEX:
                if current % C.BeatInMeasure == 0:
                    sumOfWeight[i+1] += C.AccumulativeWeight
                continue
            # other
            if previous != current:
                CIncrement += ICR
                PIncrement += ICR
            if previous < current:
                CIncrement += PR
            if previous > current:
                PIncrement += PR

            # find true duration including break
            if sequenceIndex == C.DURATIONINDEX:  # only duration sequence use this
                fixed = previous
                if seqTable[C.PITCHINDEX][i] == 0 and i > 1:
                    fixed = previous + seqTable[sequenceIndex][i-1]
                if fixed != current:
                    PIncrement += 2

            sumOfWeight[i] += PIncrement
            sumOfWeight[i+1] += CIncrement

        return sumOfWeight.astype(int)

    durationWeight = calculateWeight(C.DURATIONINDEX)
    intervalWeight = calculateWeight(C.INTERVALINDEX)
    restWeight = seqTable[C.RESTINDEX]
    accumulativeWeight = calculateWeight(C.ACCUMULATIVEINDEX)

    print("Duration Weight:")
    formattedPrint(durationWeight)
    print("Interval Weight:")
    formattedPrint(intervalWeight)
    print("Rest Weight:")
    formattedPrint(restWeight)
    print("Accumulative Weight:")
    formattedPrint(accumulativeWeight)

    print("SUM OF ABOVE: ")
    formattedPrint(2 * durationWeight + intervalWeight +
                   2 * restWeight + accumulativeWeight)
