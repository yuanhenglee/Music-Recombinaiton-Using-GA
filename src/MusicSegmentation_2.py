import numpy as np
import Constant as C
from ILBDM import ILBDM
from SimilarityMatrix import elementsClustering

def extractSignatures( target ):
    LBDM_result = ILBDM(target)
    cuttingPoint = musicSegmentation2( target, LBDM_result )
    cuttingPoint =[-1] + cuttingPoint + [target.numberOfNotes-1] # make sure first & last interval in list
    cuttingInterval = [(cuttingPoint[i]+1, cuttingPoint[i+1]+1) for i in range(len(cuttingPoint)-1)]
    print(cuttingInterval)
    elementGroups = elementsClustering( target, cuttingInterval, 0.5)
    print(elementGroups)



def checkCuttingPoint(index, LBDM, cuttingPoint, target):
    sumDuration = target.noteSeq[C.DURATIONINDEX][index]
    cut = index
    while sumDuration <= target.minSegment and index < target.numberOfNotes - 1:
        if LBDM[cut] < LBDM[index+1]:
            cut = checkCuttingPoint(index+1, LBDM, cuttingPoint, target)
            return cut
        else:
            index += 1
            sumDuration += target.noteSeq[C.DURATIONINDEX][index]
    cuttingPoint.append(cut)
    return index


def musicSegmentation2(target, LBDM):
    size_Note = LBDM.size
    # cuttingPoint = np.zeros(size_Note, dtype=int)
    cuttingPoint = []

    i = 0
    while i < size_Note-1:
        i = checkCuttingPoint(i, LBDM, cuttingPoint, target) + 1

    cuttingPoint.sort()
    print("Cutting Point = ", cuttingPoint)
    return cuttingPoint
    # target.noteSeq[C.SEGMENTATIONINDEX] = cuttingPoint