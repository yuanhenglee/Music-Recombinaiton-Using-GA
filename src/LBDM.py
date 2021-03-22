import copy
import numpy as np

PITCHINDEX = 0
DURATIONINDEX = 1
INTERVALINDEX = 2
RESTINDEX = 3


def LBDM( target ):
    # DEFINE ICR PR DURATION WEIGHT
    ICR = 1
    PR = 1

    seqTable = copy.deepcopy( target.noteSeq )

    def calculateWeight( sequenceIndex ):
        sumOfWeight = np.zeros( target.numberOfNotes )
        # ICR + PR + duration 
        for i, previous in enumerate( seqTable[sequenceIndex][:-1] ):


            current = seqTable[sequenceIndex][i+1]
            PIncrement = 0
            CIncrement = 0
            if previous != current: 
                CIncrement += ICR
                PIncrement += ICR
            if previous < current: 
                CIncrement += PR
            if previous > current: 
                PIncrement += PR

            ## find true duration including break
            fixed = previous
            if seqTable[PITCHINDEX][i] == 0 and i > 1:
                fixed = previous + seqTable[sequenceIndex][i-1]
            if fixed != current:
                PIncrement += 2

            sumOfWeight[i] += PIncrement
            sumOfWeight[i+1] += CIncrement

        return sumOfWeight
        
    durationWeight = calculateWeight( DURATIONINDEX )
    intervalWeight = calculateWeight( INTERVALINDEX )
    restWeight = calculateWeight( RESTINDEX )

    print("DURATION:")
    print(durationWeight)
    print("INTERVAL:")
    print(intervalWeight)
    print("REST:")
    print(restWeight)

    print(" SUM OF ABOVE: ")
    print( durationWeight + intervalWeight + restWeight )
