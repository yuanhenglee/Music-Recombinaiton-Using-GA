import matplotlib.pyplot as plt
import os
from zodb import ZODB
import matplotlib
matplotlib.use('Agg')


def calculateFeature(func):
    # params of func (parsedMIDI)
    x = []  # filename
    y = []  # feature
    directory = "../midi_file"
    for filename in os.listdir(directory):
        if filename.endswith(".mid"):
            name = filename[:-4]
            x.append(name)
            DBpath = './Music/'+name+'.fs'
            db = ZODB(DBpath)
            parsedMIDI = db.dbroot[name].parsedMIDI
            y.append(func(parsedMIDI))
        else:
            continue
    # draw
    x_ = [1, 2, 3, 4, 5, 6, 7, 8]
    plt.plot(x_, y)
    plt.savefig(func.__name__)
    # wsl cannot use show()
    # plt.show()


def highestNote(parsedMIDI):
    return parsedMIDI.highestNote


calculateFeature(highestNote)
