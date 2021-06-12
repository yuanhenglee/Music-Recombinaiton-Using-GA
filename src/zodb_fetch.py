from zodb import MyZODB
import Constant as C

db = MyZODB('./Music/Data.fs')
dbroot = db.dbroot
for key in dbroot.keys():
    print(key + ':', dbroot[key])
    print("Note Sequence: ", dbroot[key].parsedMIDI.noteSeq[C.PITCHINDEX])
    print("LBDM result: ", dbroot[key].result_ILBDM)
    print("Cutting point: ", dbroot[key].cuttingPoint)
    print("Possible Signature: ", dbroot[key].signaturePossibilities)
    db.close()
