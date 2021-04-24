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


def pitch_func(x, y):
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

    DF_Interval = pd.DataFrame(1/(1+distance_matrix(Interval_var, Interval_var)),
                               columns=Interval_var.index, index=Interval_var.index)

    DF_Pitch = pd.DataFrame(pitch_func(Pitch_var, Pitch_var),
                            columns=Pitch_var.index, index=Pitch_var.index)

    DF_Combine = (DF_Interval + DF_Pitch) / 2

    print(DF_Combine)

    # Display DF_SM as a matrix in a new figure window
    plt.matshow(DF_Combine)
    # Set the colormap to 'bone'.
    plt.bone()
    plt.show()
