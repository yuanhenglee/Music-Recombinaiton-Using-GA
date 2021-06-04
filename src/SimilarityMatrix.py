import numpy as np
import pandas as pd
import math
from scipy.spatial import distance_matrix
import matplotlib.pyplot as plt

import Constant as C
import Utility

# print full data frame without truncation
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 2000)
pd.set_option('display.float_format', '{:8,.2f}'.format)


def noveltyApproach(DF_similarityMatrix, percentiles, coreMatrixSize, minDistanceBetweenCutpoint):
    matrix = DF_similarityMatrix.to_numpy()
    height = matrix.shape[0]
    width = matrix.shape[1]
    score_matrix = np.zeros((height, width))
    possibleEdges = set()

    # creating a matrix "possibleEdges" which store the score on certain point
    for i in range(height):
        for j in range(width):

            # construct core matrix
            # i,j           i,j+CMS-1       i,j+2CMS-1
            # i+CMS-1,j     i+CMS-1,j+CMS-1 i+CMS-1,j+2CMS-1
            # i+2CMS-1,j
            if (i+2*coreMatrixSize-1) >= height or (j+2*coreMatrixSize-1) >= width:
                continue
            topLeft = matrix[i:i+coreMatrixSize, j:j+coreMatrixSize]
            topRight = matrix[i:i+coreMatrixSize,
                              j+coreMatrixSize:j+2*coreMatrixSize]
            botLeft = matrix[i+coreMatrixSize:i+2 *
                             coreMatrixSize, j:j+coreMatrixSize]
            botRight = matrix[i+coreMatrixSize:i+2 *
                              coreMatrixSize, j+coreMatrixSize:j+2*coreMatrixSize]
            score = 0
            for x in range(coreMatrixSize):
                for y in range(coreMatrixSize):
                    score += (1 - topLeft[x][y]) ** 2
                    score += (topRight[x][y] - 0) ** 2
                    score += (botLeft[x][y] - 0) ** 2
                    score += (1 - botRight[x][y]) ** 2

            score = 1 - (score ** 0.5)/(coreMatrixSize * 2)

            score_matrix[i+coreMatrixSize-1][j+coreMatrixSize-1] = score

    # find max score for each cutpoint
    maxScore = [(i, np.amax(score_matrix[i], axis=0)) for i in range(height)]
    maxScore.sort(key=lambda x: x[1], reverse=True)
    numberOfCutPoint = math.floor(height - height * percentiles / 100)
    cutPointcount = 0
    for i in range(height):
        tooClose = False
        for j in range(-minDistanceBetweenCutpoint, minDistanceBetweenCutpoint+1):
            if (maxScore[i][0] + j) in possibleEdges:
                tooClose = True
        if not tooClose:
            possibleEdges.add(maxScore[i][0])
            cutPointcount += 1
        if cutPointcount >= numberOfCutPoint:
            break
    # determine threshold based on possibleEdges

    # threshold = np.percentile(maxScore, percentiles)

    # possibleEdges = [maxScore[i] if maxScore[i] > threshold else 0 for i in range(height)]

    return possibleEdges


def pitchSimilarityDistance(x, y):
    x = np.asarray(x)
    m = x.shape[0]
    y = np.asarray(y)
    n = y.shape[0]

    result = np.empty([m, n])
    for i in range(m):
        for j in range(n):
            result[i][j] = 1 if x[i] == y[j] else 0
    return result

def converter(interval, noteIndexToTimeIndex ):
    return noteIndexToTimeIndex[interval[0]], noteIndexToTimeIndex[interval[1]] 

def diagonalMean( matrix, intervalA, intervalB, noteIndexToTimeIndex ):
    # notesDiff = abs((intervalB[1]-intervalB[0]) - (intervalA[1] - intervalA[0]))
    print(intervalA, " to ",end = '')
    intervalA, intervalB = converter(intervalA, noteIndexToTimeIndex), converter(intervalB, noteIndexToTimeIndex)
    print(intervalA)
    if (intervalA[1] - intervalA[0]) > (intervalB[1]-intervalB[0]): intervalA, intervalB = intervalB, intervalA
    # durationDiff = (intervalB[1]-intervalB[0]) - (intervalA[1] - intervalA[0])
    # if durationDiff > 3 or notesDiff > 3: return 0
    cells = [] 
    for i in range(intervalA[0],intervalA[1]):
        j = intervalB[0] + i - intervalA[0]
        cells.append(matrix[i][j])

        if( intervalA == (18,32) and intervalB == (41,64)):
            print( i, ",", j )
            print(matrix[i][j])
        # for k in range(durationDiff+1):
            # cells.append(matrix[i][j+k])
    if cells != []:
        return np.array(cells).mean()
    return 0



def elementsClustering( target, cuttingInterval, threshold ):
    matrix, noteIndexToTimeIndex = similarityMatrix( target )
    elementGroups = []
    for i in range( len(cuttingInterval)-1 ):
        for j in range( i+1 , len(cuttingInterval) ):
            similarity = diagonalMean( matrix, cuttingInterval[i], cuttingInterval[j], noteIndexToTimeIndex)
            if similarity >= threshold :
                elementGroups.append({cuttingInterval[i],cuttingInterval[j]})
            # print((cuttingInterval[i]),",", (cuttingInterval[j]))
            # print(similarity)
    
    for i in range( len(elementGroups) - 1 ):
        for j in range( i+1,len(elementGroups) ):
            if not elementGroups[i].isdisjoint(elementGroups[j]):
                elementGroups[i] = elementGroups[i].union(elementGroups[j])
                elementGroups[j] = set() 
        
    elementGroups = [ i for i in elementGroups if i != set()]
    return elementGroups

def similarityMatrix(target):

    expandedPitchSeq = np.empty(target.totalDuration)
    expandedIntervalSeq = np.empty(target.totalDuration)
    noteIndexToTimeIndex = np.empty(target.numberOfNotes+1, dtype=int)
    accumulativeTimeIndex = 0
    index = 0
    for i in range( target.numberOfNotes ):
        noteIndexToTimeIndex[i] = accumulativeTimeIndex
        accumulativeTimeIndex += int(target.noteSeq[C.DURATIONINDEX][i])
        for j in range( target.noteSeq[C.DURATIONINDEX][i] ):
            expandedPitchSeq[index] = target.noteSeq[C.PITCHINDEX][i]
            expandedIntervalSeq[index] = target.noteSeq[C.INTERVALINDEX][i]
            index+=1
    noteIndexToTimeIndex[target.numberOfNotes] = accumulativeTimeIndex

    expandedIntervalSeq = pd.DataFrame(expandedIntervalSeq )

    SMM_Pitch = pitchSimilarityDistance(expandedPitchSeq, expandedPitchSeq)
    SMM_Interval = distance_matrix(expandedIntervalSeq, expandedIntervalSeq)
    SMM_Interval = 1-(SMM_Interval - SMM_Interval.min())/(SMM_Interval.max()-SMM_Interval.min())
    SMM_Combined = SMM_Pitch #+ SMM_Interval /2

    plt.imshow(SMM_Combined, plt.cm.bone)
    plt.show()

    return SMM_Combined, noteIndexToTimeIndex
    
    # ! rewrite SSM function: only return matrix based on time seq now
    # Pitch_var = pd.DataFrame({
    #     "Pitch": target.noteSeq[C.PITCHINDEX]
    # })

    # Pitch_var.index = np.array([Utility.value2Pitch(i)
    #                             for i in target.noteSeq[C.PITCHINDEX]])

    # Other_var = pd.DataFrame({
    #     "Interval": target.noteSeq[C.INTERVALINDEX]
    # })

    # Other_var.index = np.array([Utility.value2Pitch(i)
    #                             for i in target.noteSeq[C.PITCHINDEX]])

    # DF_Pitch = pd.DataFrame(pitchSimilarityDistance(Pitch_var, Pitch_var),
    #                         columns=Pitch_var.index, index=Pitch_var.index)

    # df = pd.DataFrame(distance_matrix(Other_var, Other_var),
    #                   columns=Other_var.index, index=Other_var.index)
    # DF_Other = pd.DataFrame(1,
    #                         columns=Other_var.index, index=Other_var.index) - (df-df.min())/(df.max()-df.min())

    # DF_Combine = (DF_Other + DF_Pitch)/2

    # return DF_Combine.to_numpy()


    # percentage = 90
    # coreMatrixSize = 3
    # resultSize = (int)(target.numberOfNotes * (1-percentage/100))
    # result = np.zeros(resultSize, dtype=int)

    # index = 0
    # for i in noveltyApproach(DF_Combine, percentage, coreMatrixSize, 3):
    #     result[index] = i
    #     index += 1

    # result = np.sort(result)
    # print("Similarity Matrix result = ", result)

    # return result
