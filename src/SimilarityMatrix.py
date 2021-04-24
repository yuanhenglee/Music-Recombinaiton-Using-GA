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


def similarityMatrix(target):

    DF_var = pd.DataFrame.from_dict({
        "Pitch": target.noteSeq[C.PITCHINDEX],
        "Interval": target.noteSeq[C.INTERVALINDEX]
    })

    DF_var.index = np.array([Utility.value2Pitch(i)
                             for i in target.noteSeq[C.PITCHINDEX]])

    DF_SM = pd.DataFrame(1/(1+distance_matrix(DF_var, DF_var)),
                         columns=DF_var.index, index=DF_var.index)

    print(DF_var.T)
    print(DF_SM)

    # Display DF_SM as a matrix in a new figure window
    plt.matshow(DF_SM)
    # Set the colormap to 'bone'.
    plt.bone()
    plt.show()
