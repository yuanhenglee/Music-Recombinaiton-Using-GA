import numpy as np
import Constant as C


def checkCuttingPoint(start, end, cuttingPoint, LBDM):
    maxSize = (int)(LBDM.size/8) if LBDM.size/8 >= 8 else 8
    if (end - start) > maxSize:
        newCuttingPoint = start+4 + np.argmax(LBDM[start+4:end-4])
        print(newCuttingPoint)
        cuttingPoint[newCuttingPoint] = 1
        checkCuttingPoint(start, newCuttingPoint, cuttingPoint, LBDM)
        checkCuttingPoint(newCuttingPoint, end, cuttingPoint, LBDM)


def musicSegmentation(target, SM, LBDM):
    size_Note = LBDM.size
    cuttingPoint = np.zeros(size_Note, dtype=int)

    preCuttingPoint = 0
    for i in SM:
        cuttingPoint[i] = 1
        checkCuttingPoint(preCuttingPoint, i, cuttingPoint, LBDM)
        preCuttingPoint = i
    checkCuttingPoint(preCuttingPoint, size_Note-1, cuttingPoint, LBDM)

    print("Cutting Point = ", cuttingPoint)
    target.noteSeq[C.SEGMENTATIONINDEX] = cuttingPoint
