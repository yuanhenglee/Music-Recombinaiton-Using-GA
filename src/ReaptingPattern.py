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


def checkRepeat( RP1, RP2 ):
    return np.array_equal()


def findMaximalRP(CorrMatrix):
    # possibleReaptingPatterns = np.array([set() for i in range(20)])
    possibleReaptingPatterns = []
    for i in range(CorrMatrix.shape[0]-1):
        for j in range(CorrMatrix.shape[1]-1):
            if CorrMatrix[i][j] > 0 and CorrMatrix[i+1][j+1] == 0:
                # TODO what to do after finding a RP
                # Data stored in a list of sets of pairs(tuples)
                # if this kind of RP already exist :
                #   add to set
                # else:
                #   create new set

                # RP = range( index of the start of RP , index of the end of RP + 1)
                RPSet = set()
                RP1 = (1+j-CorrMatrix[i][j], 1+j)
                RP2 = (1+i-CorrMatrix[i][j], 1+i)
                possibleReaptingPatterns.append( set( [RP1, RP2] ) )
                # possibleReaptingPatterns[len(RP)].add(RP)

    print([i for i in possibleReaptingPatterns])
    for i, RPSet1 in enumerate( possibleReaptingPatterns[:-1]):
        for RPSet2 in possibleReaptingPatterns[i+1:]:
            #TODO if intersection of RPSet1 & 2 is not empty
            #   merge!!
        
    # for i in range(20):
    #     if len(possibleReaptingPatterns[i]) > 0:
    #         print("length of RP = ", i)
    #         print(possibleReaptingPatterns[i])
    #         print()


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

    print("Maximal Repeating Pattern:")
    print("1. based on pitch: ")
    findMaximalRP(pitchCorrMatrix)
    print("2. based on pitch interval: ")
    findMaximalRP(intervalCorrMatrix)
    print("3. Augmentation & Diminution: ")
    findMaximalRP(ADCorrMatrix)
