from Fitness import updateFitness
from Fitness import elementsTransition
from zodb import ZODB
import Constant as C
import Fitness
from ILBDM import ILBDM
import sys
import Fitness
import numpy as np

db = ZODB(sys.argv[1])
dbroot = db.dbroot
print(dbroot.keys())
for key in dbroot.keys():
    individual = dbroot[key]
    # individual.parsedMIDI.printMIDI()
    # print(elementsTransition(individual))
    # print(individual.signature)
    # print(individual.parsedMIDI.noteSeq[C.ELEMENTINDEX])
    for tree in individual.tree_list:
        print(tree.id, len(tree.pitchSeq))
    # print(np.unique(individual.parsedMIDI.noteSeq[C.ELEMENTINDEX]))
    # Fitness.updateFitness(individual)
    print(individual.fitness_detail)
    # print(individual.fitness)
    # Fitness.updateFitness(individual)
    # break
    # result_ILBDM = ILBDM(individual.parsedMIDI)
    # print(result_ILBDM)
    count = 1
    element_set = {} 
    for i in range(len(dbroot[key].parsedMIDI.noteSeq[C.ELEMENTINDEX])):
        if not individual.parsedMIDI.noteSeq[C.ELEMENTINDEX][i] in element_set:
            print(count, end=" ")
            element_set[individual.parsedMIDI.noteSeq[C.ELEMENTINDEX][i]] = count
            count+=1
        else:
            print(element_set[individual.parsedMIDI.noteSeq[C.ELEMENTINDEX][i]], end = " ")
            
    print(element_set)


db.close()
