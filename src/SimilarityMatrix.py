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


def noveltyApproach(DF_similarityMatrix, threshold, coreMatrixSize):
    matrix = DF_similarityMatrix.to_numpy()
    height = matrix.shape[0]
    width = matrix.shape[1]
    possibleEdges = [0 for i in range(height)]
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

            score = (topLeft.mean()+botRight.mean() -
                     topRight.mean()-botLeft.mean())/2

            if score > threshold:
                possibleEdges[i+coreMatrixSize] += score
                # print(i+coreMatrixSize," ",j+coreMatrixSize)
                # print( score)
                # print( matrix[i:i+2*coreMatrixSize, j:j+2*coreMatrixSize])
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

    Interval_var = pd.DataFrame({
        "Interval": target.noteSeq[C.INTERVALINDEX]
    })

    Interval_var.index = np.array([Utility.value2Pitch(i)
                                   for i in target.noteSeq[C.PITCHINDEX]])

    Pitch_var = pd.DataFrame({
        "Pitch": target.noteSeq[C.PITCHINDEX]
    })

    Pitch_var.index = np.array([Utility.value2Pitch(i)
                                for i in target.noteSeq[C.PITCHINDEX]])

    df = pd.DataFrame(distance_matrix(Interval_var, Interval_var),
                      columns=Interval_var.index, index=Interval_var.index)
    DF_Interval = pd.DataFrame(1,
                               columns=Interval_var.index, index=Interval_var.index) - (df-df.min())/(df.max()-df.min())

    DF_Pitch = pd.DataFrame(pitchSimilarityDistance(Pitch_var, Pitch_var),
                            columns=Pitch_var.index, index=Pitch_var.index)

    DF_Combine = (DF_Interval + DF_Pitch) / 2

    print(DF_Combine)

    for size in range(1, 4):
        print("size: ", size)
        for i in noveltyApproach(DF_Combine, 0.5, size):
            print("%2.1f " % i, end='')
        print()

    # Display DF_SM as a matrix in a new figure window
    plt.matshow(DF_Combine)
    # Set the colormap to 'bone'.
    plt.bone()
    plt.show()
