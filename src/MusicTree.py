import numpy as np
from ILBDM import ILBDM
import Constant as C


class treeNode:
    def __init__(self, _pitchSeq, _durationSeq, LBDM):
        if len(_pitchSeq) != len(_durationSeq) or len(_pitchSeq) != len(LBDM):
            print("Input error")

        self.pitchSeq = _pitchSeq
        self.durationSeq = _durationSeq
        self.length = len(_pitchSeq)

        # print(LBDM)
        if len(LBDM) >= 2:
            maxIndex = np.argmax(LBDM[:-1])
            # print("left:")
            self.left = treeNode(
                _pitchSeq[:maxIndex+1], _durationSeq[:maxIndex+1], LBDM[:maxIndex+1])
            # print("right:")
            self.right = treeNode(
                _pitchSeq[maxIndex+1:], _durationSeq[maxIndex+1:], LBDM[maxIndex+1:])


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
    test = treeNode(pitchSeq, durationSeq, LBDM_result)
