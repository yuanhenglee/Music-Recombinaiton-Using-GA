from zodb import ZODB
import Constant as C

db = ZODB('./Music/刻在我心底的名字.fs')
dbroot = db.dbroot
print(dbroot.keys())
for key in dbroot.keys():
    print(key)
    print(dbroot[key])

db.close()
