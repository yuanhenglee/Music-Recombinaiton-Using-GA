import numpy as np
import Constant as C


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
    cuttingPoint[cut] = 1
    print(cut)
    return index


def musicSegmentation2(target, LBDM):
    size_Note = LBDM.size
    cuttingPoint = np.zeros(size_Note, dtype=int)

    i = 0
    while i < size_Note-1:
        i = checkCuttingPoint(i, LBDM, cuttingPoint, target) + 1

    print("Cutting Point = ", cuttingPoint)
    target.noteSeq[C.SEGMENTATIONINDEX] = cuttingPoint
