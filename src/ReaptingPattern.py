import numpy as np
import Constant as C

# for printing
from Utility import formattedPrint
from tabulate import tabulate


def corrMatrix( cmpFactors ):

    cmpFactors = list( cmpFactors )
    
    matrix = np.zeros((len(cmpFactors),len(cmpFactors)))

    for i,p1 in enumerate(cmpFactors):
        for j,p2 in enumerate(cmpFactors[:i]):
            if p1 == p2:
                    matrix[i][j] = matrix[i-1][j-1] + 1 if i > 0 and j > 0 else 1 

    return matrix.astype(int)


def findReaptingPattern( target ):

    # seqTable = copy.deepcopy(target.noteSeq)

    # step 1: find based on pitch sequence
    pitchCorrMatrix = corrMatrix( zip( target.noteSeq[C.PITCHINDEX], target.noteSeq[C.DURATIONINDEX] ) )

    print("Correlative Matrix based on pitch & duration sequence")
    print( tabulate( pitchCorrMatrix ,tablefmt="rst", headers = target.noteSeq[C.PITCHINDEX]))
    # [formattedPrint(i.tolist()) for i in pitchCorrMatrix]