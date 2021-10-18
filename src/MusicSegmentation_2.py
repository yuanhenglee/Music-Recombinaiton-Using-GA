import numpy as np
import Constant as C
from ILBDM import ILBDM
from SimilarityMatrix import elementsClustering


def hashElementNumber(target, name):
    for i, value in enumerate(target.noteSeq[C.ELEMENTINDEX]):
        value = hash((name, value))
        target.noteSeq[C.ELEMENTINDEX][i] = value


def extractSignatures(target):
    # LBDM_result = ILBDM(target)
    # cuttingPoint = musicSegmentation2(target, LBDM_result)
    # # make sure first & last interval in list
    # cuttingPoint = [-1] + cuttingPoint + [target.numberOfNotes-1]
    element_seq = target.noteSeq[C.ELEMENTINDEX]
    cuttingInterval = []
    start = 0
    for i in range(len(element_seq)):
        if i == len(element_seq)-1 or element_seq[i] != element_seq[i+1]:
            end = i+1
            cuttingInterval.append((start, end))
            start = i+1

    # cuttingInterval = [(cuttingPoint[i]+1, cuttingPoint[i+1]+1)
    #                    for i in range(len(cuttingPoint)-1)]
    possibleSignatures = elementsClustering(target, cuttingInterval, 0.8)
    if possibleSignatures != []:
        # elements in the same element group have the same element number
        for signature in possibleSignatures:
            element_number = -1
            for (i, j) in signature:
                if element_number == -1:
                    element_number = element_seq[i]
                element_seq[i:j] = element_number


def tooClose(cuttingPoint, index, minSegment):
    for i in range(1, minSegment):
        if index-i in cuttingPoint or index+i in cuttingPoint:
            return True
    return False


def checkCuttingPoint(LBDM, target):
    index_lbdm = [(i, LBDM[i]) for i in range(len(LBDM))]
    cuttingPoint = []
    index_lbdm = sorted(index_lbdm, key=lambda x: x[1])
    while(len(index_lbdm) > 0):
        index_selected = index_lbdm.pop()
        if not tooClose(cuttingPoint, index_selected[0], target.minSegment):
            cuttingPoint.append(index_selected[0])
    return cuttingPoint
    # return cuttingPoint
# def checkCuttingPoint(index, LBDM, cuttingPoint, target):
#     sumDuration = target.noteSeq[C.DURATIONINDEX][index]
#     cut = index
#     while sumDuration <= target.minSegment and index < target.numberOfNotes - 1:
#         if LBDM[cut] < LBDM[index+1]:
#             cut = checkCuttingPoint(index+1, LBDM, cuttingPoint, target)
#             return cut
#         else:
#             index += 1
#             sumDuration += target.noteSeq[C.DURATIONINDEX][index]
#     cuttingPoint.append(cut)
#     return index


def musicSegmentation2(target, LBDM):
    size_Note = LBDM.size
    cuttingPoint = checkCuttingPoint(LBDM, target)
    # cuttingPoint = np.zeros(size_Note, dtype=int)
    # cuttingPoint = [target.numberOfNotes-1]

    # i = 0
    # while i < size_Note-1:
    #     i = checkCuttingPoint(i, LBDM, cuttingPoint, target) + 1

    cuttingPoint.sort()
    # print("Cutting Point = ", cuttingPoint)
    '''
    use cutting point to divide element (noteSeq[C.ELEMENTINDEX])
    [0. 0. 0. 0. 0. 0. 0. 0. 0. 1. 1. 1. 1. 1. 1. 1. 2. 2. 2. 2. 2. 2. 2. 2. 2. 2. 2. 
    3. 3. 3. 3. 3. 3. 3. 3. 4. 4. 4. 4. 4. 4. 4. 4. 4. 4. 4. 5. 5. 5. 5. 5. 5. 5. 5. 5. 
    6. 6. 6. 6. 6. 6. 6. 6. 6. 7. 7. 7. 7. 7. 7. 7. 7. 8.]
    '''
    start_index = 0
    for i, index in enumerate(cuttingPoint):
        target.noteSeq[C.ELEMENTINDEX][start_index:index+1] = i
        start_index = index + 1
    return cuttingPoint
    # target.noteSeq[C.SEGMENTATIONINDEX] = cuttingPoint


def musicTree(target, LBDM):
    i = 0


if __name__ == "__main__":
    import sys
    from mido import MidiFile
    from Preprocess import ProcessedMIDI

    path = sys.argv[1]
    mid = MidiFile(path)
    parsedMIDI = ProcessedMIDI(mid)
    LBDM_result = ILBDM(parsedMIDI)
    cuttingPoint = musicSegmentation2(
        parsedMIDI, LBDM_result)
    # signaturePossibilities = extractSignatures(
    #     parsedMIDI)
    print(LBDM_result)
    print(cuttingPoint)
    # print(signaturePossibilities)
