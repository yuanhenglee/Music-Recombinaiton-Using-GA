from zodb import MyZODB, transaction
from music import Music

db = MyZODB('./Music/Data.fs')
dbroot = db.dbroot
dbroot['Full Stop'] = Music('../midi_file/FullStop.mid', 'Full Stop')
transaction.commit()
db.close()
