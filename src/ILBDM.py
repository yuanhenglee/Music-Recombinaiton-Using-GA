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
    totalWeight = 2*durationWeight + intervalWeight + 2*restWeight + accumulativeWeight

    # print("Duration Weight:")
    # formattedPrint(durationWeight)
    # print("Interval Weight:")
    # formattedPrint(intervalWeight)
    # print("Rest Weight:")
    # formattedPrint(restWeight)
    # print("Accumulative Weight:")
    # formattedPrint(accumulativeWeight)

    # print("SUM OF ABOVE: ")
    # formattedPrint(2 * durationWeight + intervalWeight +
    #                2 * restWeight + accumulativeWeight)

    # print("ILBDM result = ", totalWeight)
    return totalWeight

# TODO


def ILBDM_elementary_noteSeq(noteSeq):
    # DEFINE ICR PR DURATION WEIGHT
    ICR = 1
    PR = 1

    # seqTable = copy.deepcopy(noteSeq)

    durationScore = np.zeros(len(noteSeq[0]))
    intervalScore = np.zeros(len(noteSeq[0]))
    restScore = np.zeros(len(noteSeq[0]))

    intervalSeq = np.zeros(len(noteSeq[0]))
    restSeq = np.zeros(len(noteSeq[0]))

    for i, curPitch in enumerate(noteSeq[C.PITCHINDEX][:-1]):
        nextPitch = noteSeq[C.PITCHINDEX][i+1]
        # cutpoint might appear between each break
        if curPitch == 0:
            restSeq[i] = noteSeq[C.DURATIONINDEX][i]
        elif nextPitch == 0 and i + 2 < len(noteSeq[0]):
            nextNextPitch = noteSeq[C.PITCHINDEX][i+2]
            restSeq[i] = noteSeq[C.DURATIONINDEX][i+1]
            intervalSeq[i]\
                = abs(nextNextPitch - curPitch)
            intervalSeq[i+1]\
                = abs(nextNextPitch - curPitch)
        elif nextPitch == 0 and i+2 == len(noteSeq[0]):
            intervalSeq[i] = 0
        else:
            intervalSeq[i] = abs(nextPitch - curPitch)

    for i in range(len(noteSeq[0]) - 1):
        D_PIncrement = 0
        D_CIncrement = 0
        I_PIncrement = 0
        I_CIncrement = 0
        # Duration score
        if noteSeq[C.DURATIONINDEX][i] != noteSeq[C.DURATIONINDEX][i+1]:
            D_CIncrement += ICR
            D_PIncrement += ICR
        if noteSeq[C.DURATIONINDEX][i] < noteSeq[C.DURATIONINDEX][i+1]:
            D_CIncrement += PR
        if noteSeq[C.DURATIONINDEX][i] > noteSeq[C.DURATIONINDEX][i+1]:
            D_PIncrement += PR

        # Interval score
        if intervalSeq[i] != intervalSeq[i+1]:
            I_CIncrement += ICR
            I_PIncrement += ICR
        if intervalSeq[i] < intervalSeq[i+1]:
            I_CIncrement += PR
        if intervalSeq[i] > intervalSeq[i+1]:
            I_PIncrement += PR

        # find true duration including break
        fixed = noteSeq[C.DURATIONINDEX][i]
        if noteSeq[C.PITCHINDEX][i] == 0 and i > 1:
            fixed = noteSeq[C.DURATIONINDEX][i] + noteSeq[C.DURATIONINDEX][i-1]
        if fixed != noteSeq[C.DURATIONINDEX][i+1]:
            D_PIncrement += 2

        durationScore[i] += D_PIncrement
        durationScore[i+1] += D_CIncrement
        intervalScore[i] += I_PIncrement
        intervalScore[i+1] += I_CIncrement

    restWeight = restSeq
    totalWeight = 2*durationScore + intervalScore + 2*restWeight
    return totalWeight
