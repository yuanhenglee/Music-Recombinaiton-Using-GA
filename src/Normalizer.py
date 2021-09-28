from zodb import ZODB, transaction
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, Normalizer, scale

import Constant as C

df = pd.DataFrame()
df["F1"] = [1, 2, 3, 4]
df["F2"] = [10, 20, 30, 30]

test = [2, 0.4]
test2 = np.reshape(test, (-1, 1))
test2 = np.insert(test2, [1], [0]*3, axis=1)
# print(test2)

df_standard = (StandardScaler().fit_transform(df))
print(df_standard.T)

df_normalized = (Normalizer().fit_transform(df_standard.T)+1)/2
print(df_normalized)


std_scal = StandardScaler().fit(df)
test_std = std_scal.transform(test2.T).T
print(test_std)
nor_scal = Normalizer().fit(df_standard.T)
test_nor = (nor_scal.transform(test_std)+1)/2
print(test_nor)
ans = [test_nor[i][0] for i in range(0, 2)]
print(ans)

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
