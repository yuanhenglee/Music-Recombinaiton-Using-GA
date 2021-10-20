from Fitness import updateFitness
from zodb import ZODB
import Constant as C
import Fitness
from ILBDM import ILBDM
import sys

db = ZODB(sys.argv[1])
dbroot = db.dbroot
print(dbroot.keys())
for key in dbroot.keys():
    individual = dbroot[key]
    # print(individual.signature)
    # print(individual.parsedMIDI.noteSeq[C.ELEMENTINDEX])
    # for tree in individual.tree_list:
    #     print(tree.id)
    print(individual.df_features)
    print(individual.df_features_std)
    print(individual.fitness_detail)
    print(individual.fitness)
    # Fitness.updateFitness(individual)
    # break
    # result_ILBDM = ILBDM(individual.parsedMIDI)
    # print(result_ILBDM)
    # for i in range(len(dbroot[key].parsedMIDI.noteSeq[C.ELEMENTINDEX])):
    #     if i == 0:
    #         print(0, end=' ')
    #     else:
    #         if individual.parsedMIDI.noteSeq[C.ELEMENTINDEX][i] != individual.parsedMIDI.noteSeq[C.ELEMENTINDEX][i-1]:
    #             print(1, end=" ")
    #         else:
    #             print(0, end=' ')


db.close()
