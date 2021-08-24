import numpy as np
from ILBDM import ILBDM
import Constant as C
import copy


class treeNode:
    def __init__(self, _startIndex, _pitchSeq, _durationSeq, _LBDM=[]):
        if len(_pitchSeq) == len(_durationSeq) or len(_pitchSeq) == len(_LBDM):
            self.pitchSeq = _pitchSeq
            self.durationSeq = _durationSeq
            self.startIndex = _startIndex
            self.LBDM = _LBDM
            self.length = sum(_durationSeq)
            self.left = None
            self.right = None
            self.hashTable = {}

            # print(LBDM)
            if len(_LBDM) >= 2:
                if self.length not in self.hashTable:
                    self.hashTable[self.length] = set()
                self.hashTable[self.length].add(self)

                maxIndex = np.argmax(_LBDM[:-1])
                # print("left:")
                self.left = treeNode(
                    self.startIndex, _pitchSeq[:maxIndex+1], _durationSeq[:maxIndex+1], _LBDM[:maxIndex+1])
                # print("right:")
                self.right = treeNode(
                    self.startIndex + maxIndex+1, _pitchSeq[maxIndex+1:], _durationSeq[maxIndex+1:], _LBDM[maxIndex+1:])

                self.updateHashTable(self.left.hashTable)
                self.updateHashTable(self.right.hashTable)

    def copyNode(self, otherNode):
        self.pitchSeq = otherNode.pitchSeq
        self.durationSeq = otherNode.durationSeq
        self.length = otherNode.length
        self.startIndex = otherNode.startIndex
        self.LBDM = otherNode.LBDM
        self.hashTable = copy.deepcopy(otherNode.hashTable)
        self.left = treeNode(0, [], [])
        self.right = treeNode(0, [], [])
        if otherNode.left != None:
            self.left.copyNode(otherNode.left)
        else:
            self.left = None
        if otherNode.right != None:
            self.right.copyNode(otherNode.right)
        else:
            self.right = None

    def updateHashTable(self, newHashTable):
        for k, v in newHashTable.items():
            if k not in self.hashTable:
                self.hashTable[k] = set()
            self.hashTable[k] = set.union(self.hashTable[k], v)


if __name__ == "__main__":

    import sys
    from mido import MidiFile
    from Preprocess import ProcessedMIDI

    path = sys.argv[1]
    mid = MidiFile(path)
    parsedMIDI = ProcessedMIDI(mid)
    LBDM_result = ILBDM(parsedMIDI)
    pitchSeq = parsedMIDI.noteSeq[C.PITCHINDEX]
    durationSeq = parsedMIDI.noteSeq[C.DURATIONINDEX]
    test = treeNode(0, pitchSeq, durationSeq, LBDM_result)
    ''' test copyNode '''
    test2 = treeNode(0, [], [])
    test2.copyNode(test)
    ''' test hashTable '''
    print(test.hashTable)
    # test2.hashTable.pop(103, None)
    # print(103 in test.hashTable)
