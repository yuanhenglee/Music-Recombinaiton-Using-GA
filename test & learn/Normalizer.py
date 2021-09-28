from zodb import ZODB, transaction
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, Normalizer, scale

import Constant as C

C.NUMBER_FEATURES = 1

df = pd.DataFrame()
df["F1"] = [1, 2, 3, 4]
df["F2"] = [10, 20, 30, 30]

test = [2, 5]
test2 = np.reshape(test, (-1, 1))
test2 = np.insert(test2, [1], [0]*3, axis=1)
# print(test2)

df_standard = (StandardScaler().fit_transform(df))
print(df_standard.T)

df_normalized = (Normalizer().fit_transform(df_standard.T)+1)/2
# print(df_normalized)

std_max = [df_standard.T[i].max() for i in range(df_standard.T.shape[0])]
std_min = [df_standard.T[i].min() for i in range(df_standard.T.shape[0])]
std_range = [std_max[i] - std_min[i] for i in range(len(std_max))]
print(std_max)
print(std_min)
print(std_range)

std_scal = StandardScaler().fit(df)
test_std = std_scal.transform(test2.T).T
test_std = [test_std[i][0] for i in range(test_std.shape[0])]
print(test_std)

for i in range(len(test_std)):
    test_std[i] = (test_std[i] - std_min[i])/std_range[i]

print(test_std)


# # store into zodb
# test = [0.5]*22
# print(test)
# test2d = np.reshape(test, (-1, 1))
# test2d = np.insert(test2d, [1], []*(C.NUMBER_SONGS-1), axis=1)
# print(test2d)

# dbpath = "./Transformer/StandardScaler.fs"
# db = ZODB(dbpath)
# dbroot = db.dbroot
# standard_scaler = dbroot[0]
# db2 = ZODB("./Transformer/Normalizer.fs")
# normalizer = db2.dbroot[0]

# test_stdize = standard_scaler.transform(test2d.T).T
# print(test_stdize)
# test_normalize = (normalizer.transform(test_stdize.T).T+1)/2
# print(test_normalize)
# ans = [test_normalize[i][0] for i in range(test_normalize.shape[0])]
# print(ans)

# db.close()
# db2.close()
