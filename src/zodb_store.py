from zodb import ZODB, transaction
from music import Music

import os


def storeIntoDB(name):
    dbpath = './Music/'+name+'.fs'
    midipath = '../midi_file/'+name+'.mid'
    db = ZODB(dbpath)
    dbroot = db.dbroot
    dbroot[name] = Music(midipath, name)
    transaction.commit()
    db.close()


directory = '../midi_file'
for filename in os.listdir(directory):
    if filename.endswith(".mid"):
        storeIntoDB(filename[:-4])
    else:
        continue
