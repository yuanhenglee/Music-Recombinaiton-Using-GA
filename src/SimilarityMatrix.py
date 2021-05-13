import numpy as np
import pandas as pd
from scipy.spatial import distance_matrix
import matplotlib.pyplot as plt

import Constant as C
import Utility

# print full data frame without truncation
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 2000)
pd.set_option('display.float_format', '{:8,.2f}'.format)


def noveltyApproach(DF_similarityMatrix, percentiles, coreMatrixSize):
    matrix = DF_similarityMatrix.to_numpy()
    height = matrix.shape[0]
    width = matrix.shape[1]
    score_matrix = np.zeros((height,width))
    possibleEdges = np.zeros(height)

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
    maxScore = np.amax(score_matrix, axis = 0)
    # determine threshold based on possibleEdges
    threshold = np.percentile(maxScore, percentiles)

    possibleEdges = [maxScore[i] if maxScore[i] > threshold else 0 for i in range(height)]

    # TEST
    print( "Threshold", threshold )


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


def similarityMatrix(target):

    Pitch_var = pd.DataFrame({
        "Pitch": target.noteSeq[C.PITCHINDEX]
    })

    Pitch_var.index = np.array([Utility.value2Pitch(i)
                                for i in target.noteSeq[C.PITCHINDEX]])

    Other_var = pd.DataFrame({
        "Interval": target.noteSeq[C.INTERVALINDEX]
    })

    Other_var.index = np.array([Utility.value2Pitch(i)
                                for i in target.noteSeq[C.PITCHINDEX]])

    DF_Pitch = pd.DataFrame(pitchSimilarityDistance(Pitch_var, Pitch_var),
                            columns=Pitch_var.index, index=Pitch_var.index)

    df = pd.DataFrame(distance_matrix(Other_var, Other_var),
                      columns=Other_var.index, index=Other_var.index)
    DF_Other = pd.DataFrame(1,
                            columns=Other_var.index, index=Other_var.index) - (df-df.min())/(df.max()-df.min())

    DF_Combine = (DF_Other + DF_Pitch)/2

    print(DF_Combine)

    for size in range(1, 4):
        print("size: ", size)
        for i in noveltyApproach(DF_Combine, 90, size):
            print("%2.1f " % i, end='')
        print()

    # Display DF_SM as a matrix in a new figure window
    plt.matshow(DF_Combine)
    # Set the colormap to 'bone'.
    plt.bone()
    plt.show()
