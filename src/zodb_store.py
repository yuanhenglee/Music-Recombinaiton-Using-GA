from zodb import MyZODB, transaction
from music import Music

db = MyZODB('./Music/刻在我心底的名字.fs')
dbroot = db.dbroot
dbroot['刻在我心底的名字'] = Music('../midi_file/刻在我心底的名字.mid', '刻在我心底的名字')
transaction.commit()
db.close()
