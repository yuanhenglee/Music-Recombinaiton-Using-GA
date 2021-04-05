import numpy as np
import Constant as C

# for printing
import Utility
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
    pitchInName = np.array([ Utility.value2Pitch(i) for i in target.noteSeq[C.PITCHINDEX] ])
    print( tabulate( np.c_[ pitchInName.reshape((pitchInName.size,1)) , pitchCorrMatrix ] ,tablefmt="rst", headers = pitchInName ) )

    print("Maximal Reapting Pattern:")

    possibleReaptingPatterns = set()

    for i in range( pitchCorrMatrix.shape[0]-1 ):
        for j in range( pitchCorrMatrix.shape[1]-1 ):
            if pitchCorrMatrix[i][j] > 0 and pitchCorrMatrix[i+1][j+1] == 0:
                RP = range( j-pitchCorrMatrix[i][j] , j+1 )
                possibleReaptingPatterns.add( RP )

    print( possibleReaptingPatterns )
    for reaptingPattern in possibleReaptingPatterns:
        for i in reaptingPattern:
            
                

    