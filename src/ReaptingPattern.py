import numpy as np
import Constant as C

# for printing
import Utility
from tabulate import tabulate


def corrMatrix(cmpFactors):

    cmpFactors = list(cmpFactors)

    matrix = np.zeros((len(cmpFactors), len(cmpFactors)))

    for i, p1 in enumerate(cmpFactors):
        for j, p2 in enumerate(cmpFactors[:i]):
            if p1 == p2:
                matrix[i][j] = matrix[i-1][j-1] + 1 if i > 0 and j > 0 else 1

    return matrix.astype(int)


def findMaximalRP(CorrMatrix):
    possibleReaptingPatterns = np.array([set() for i in range(20)])
    for i in range(CorrMatrix.shape[0]-1):
        for j in range(CorrMatrix.shape[1]-1):
            if CorrMatrix[i][j] > 0 and CorrMatrix[i+1][j+1] == 0:
                RP = range(1+j-CorrMatrix[i][j], 1+j)
                # RP = range( index of the start of RP , index of the end of RP + 1)
                possibleReaptingPatterns[len(RP)].add(RP)

    for i in range(20):
        if len(possibleReaptingPatterns[i]) > 0:
            print("length of RP = ", i)
            print(possibleReaptingPatterns[i])
            print()


def printCorrMatrix(target, CorrMatrix):
    pitchInName = np.array([Utility.value2Pitch(i)
                            for i in target.noteSeq[C.PITCHINDEX]])
    print(tabulate(np.c_[pitchInName.reshape(
        (pitchInName.size, 1)), CorrMatrix], tablefmt="rst", headers=pitchInName))


def findReaptingPattern(target):

    # seqTable = copy.deepcopy(target.noteSeq)

    # step 1: find based on pitch sequence
    pitchCorrMatrix = corrMatrix(
        zip(target.noteSeq[C.PITCHINDEX], target.noteSeq[C.DURATIONINDEX]))

    # step 2: find based on pitch interval sequence
    intervalCorrMatrix = corrMatrix(
        zip(target.noteSeq[C.INTERVALINDEX], target.noteSeq[C.DURATIONINDEX]))

    # step 3: Augmentation & Diminution (AD) (find only based on pitch interval sequence)
    ADCorrMatrix = corrMatrix(target.noteSeq[C.PITCHINDEX])

    # print correlative matrix
    print("Correlative Matrix based on pitch & duration sequence")
    printCorrMatrix(target, pitchCorrMatrix)
    print("Correlative Matrix based on pitch interval & duration sequence")
    printCorrMatrix(target, intervalCorrMatrix)
    print("Correlative Matrix only based on pitch interval sequence (Augmentation & Diminution)")
    printCorrMatrix(target, ADCorrMatrix)

    print("Maximal Reapting Pattern:")
    print("1. based on pitch: ")
    findMaximalRP(pitchCorrMatrix)
    print("2. based on pitch interval: ")
    findMaximalRP(intervalCorrMatrix)
    print("3. Augmentation & Diminution: ")
    findMaximalRP(ADCorrMatrix)
