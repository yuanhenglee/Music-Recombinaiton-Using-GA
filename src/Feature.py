import matplotlib.pyplot as plt
import numpy as np
import Utility
import os
import Constant as C
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
            featureResult = func( parsedMIDI )
            print( featureResult )
            y.append( featureResult )
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


def calPitchRatio( parsedMIDI ):
    intervalCount = { 0:0, 0.5:0 , 1:0, 1.5:0, 2:0, 3:0, 3.5:0, 4:0, 4.5:0, 5:0, 5.5:0, 6:0, 7:0 }
    interval2Name = {   
                        0:"unison",
                        0.5:"m2",
                        1:"M2",
                        1.5:"m3",
                        2:"M3",
                        3:"P4",
                        3.5:"dim5",
                        4:"P5",
                        4.5:"m6",
                        5:"M6",
                        5.5:"m7",
                        6:"M7",
                        7:"octave"
                    }
    # sort intervals into 13 categories
    # unison    m2  M2  m3  M3  P4  dim5    P5  m6  M6  m7  M7  octave
    # 0         0.5 1   1.5 2   3   3.5     4   4.5 5   5.5 6   7
    for interval in parsedMIDI.noteSeq[C.INTERVALINDEX]:
        if interval //7 >= 1 and interval % 7 == 0:
            intervalCount[7] += 1
        else: 
            intervalCount[interval%7] += 1
    
    intervalFreq = {}
    for k,v in intervalCount.items():
        intervalFreq[ interval2Name[k] ] = v / parsedMIDI.noteSeq[C.INTERVALINDEX].shape[0]

    return intervalFreq 

# 21 feature from "Towards Melodic Extension Using Genetic Algorithms"

# Pitch features
def pitchVariety( parsedMIDI ):
    numberOfDistinctNote = len( np.unique( parsedMIDI.noteSeq[C.PITCHINDEX] ) )
    variety = numberOfDistinctNote / parsedMIDI.numberOfNotes
    return variety

def pitchRange( parsedMIDI ):
    return ( parsedMIDI.highestNote - parsedMIDI.lowestNote )/14 # different from  "Toward..." due to different in encode

# Tonality features
def keyCentered( parsedMIDI ):
    primaryPitch = Utility.countTonicDominant( parsedMIDI.noteSeq[C.PITCHINDEX] )
    return primaryPitch/parsedMIDI.numberOfNotes

def NonScaleNotes( parsedMIDI ):
    nonScaleNotes =Utility.countNonScaleNote( parsedMIDI.noteSeq[C.PITCHINDEX] )
    return nonScaleNotes/parsedMIDI.numberOfNotes

def dissonantIntervals( parsedMIDI ):
    sumOfDissonantRating = 0
    print( parsedMIDI.noteSeq[C.INTERVALINDEX] )
    
    for i in parsedMIDI.noteSeq[C.INTERVALINDEX]:
        if i == 6 or i == 11 or i >=13 or not i.is_integer():
            sumOfDissonantRating += 1
        elif i == 10:
            sumOfDissonantRating += 0.5
    return sumOfDissonantRating/parsedMIDI.numberOfNotes

calculateFeature(dissonantIntervals)