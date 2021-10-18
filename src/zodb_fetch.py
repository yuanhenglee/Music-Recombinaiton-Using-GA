from zodb import ZODB
import Constant as C
from ILBDM import ILBDM
import sys

db = ZODB(sys.argv[1])
dbroot = db.dbroot
print(dbroot.keys())
for key in dbroot.keys():
    individual = dbroot[key]
    result_ILBDM = ILBDM(individual.parsedMIDI)
    print(result_ILBDM)
    for i in range(len(dbroot[key].parsedMIDI.noteSeq[C.ELEMENTINDEX])):
        if i == 0:
            print(0, end=' ')
        else:
            if individual.parsedMIDI.noteSeq[C.ELEMENTINDEX][i] != individual.parsedMIDI.noteSeq[C.ELEMENTINDEX][i-1]:
                print(1, end=" ")
            else:
                print(0, end=' ')


db.close()
