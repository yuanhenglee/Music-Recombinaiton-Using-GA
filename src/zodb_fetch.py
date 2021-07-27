from zodb import ZODB
import Constant as C

db = ZODB('./Music/刻在我心底的名字.fs')
dbroot = db.dbroot
for key in dbroot.keys():
    print(key + ':', dbroot[key])
    print("Note Sequence: ", dbroot[key].parsedMIDI.noteSeq[C.PITCHINDEX])
    print("LBDM result: ", dbroot[key].result_ILBDM)
    print("Cutting point: ", dbroot[key].cuttingPoint)
    print("Possible Signature: ", dbroot[key].signaturePossibilities)
    db.close()
