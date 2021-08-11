from zodb import ZODB
import Constant as C

db = ZODB('./Music_result/test.fs')
dbroot = db.dbroot
for key in dbroot.keys():
    print(key + ':', dbroot[key])
    print("Note Sequence: ", dbroot[key].parsedMIDI.noteSeq[C.PITCHINDEX])
    for i in range(20):
        print(dbroot[key].features[i])
    db.close()
