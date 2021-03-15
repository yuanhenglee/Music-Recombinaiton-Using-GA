from mido import MidiFile, Message
from math import gcd
import numpy as np

class eventPair:
    def __init__( self, firstEvent, secondEvent ):
        self.firstEvent = firstEvent
        self.secondEvent = secondEvent

# check if two events can possiblely be a pair
def isPair( a, b ):
    if a.channel == b.channel and a.note == b.note :
        return True;
    return False;

def exploreMIDI( mid ):

    timeSet = [] # store possible periods
    totalTime = 0
    lowest = 109
    highest = 20

    for i, track in enumerate(mid.tracks):
        for j, event in enumerate(track):
            if event.time > 0:
                timeSet.append(event.time)
                totalTime += event.time

                lowest = event.note if event.note < lowest else lowest
                highest = event.note if event.note > highest else highest



    # drop first event's delta time
    timeSet.pop(0)
    res = gcd(*timeSet)
    return  res  , totalTime//res , lowest , highest


def parseMIDI( mid ):

    # DEFINE ENCODING
    MINLENGTH , MAXNOTE , LOWESTNOTE , HIGHESTNOTE = exploreMIDI( mid )
    
    OFFSET = 1 - LOWESTNOTE
    BREAK = 0
    SUSTAIN = HIGHESTNOTE +OFFSET + 1

    # initialize
    noteSeq = np.full( MAXNOTE , BREAK )
    curTime = -1 # will be 0 when we find the first ON event

    for i, track in enumerate(mid.tracks):
        print('Track {}: {}'.format(i, track.name))
        for j,firstEvent in enumerate(track):

            if firstEvent.type == "note_on" and curTime == -1: curTime = 0 # first note-on
            else: curTime += firstEvent.time

            if ( firstEvent.type == "note_on" ):
                # find note_off event for this one
                deltaTime = 0
                pairFound = False
                for secondEvent in track[j+1:-1]:
                    deltaTime = deltaTime + secondEvent.time;
                    if secondEvent.type == "note_off" and isPair (firstEvent,secondEvent):

                        # test
                        print(firstEvent)
                        print(secondEvent)
                        print("delta time = " + str(deltaTime) )
                        print("current Time = " + str(curTime) + "\n---\n" )
                        # test

                        start = int(curTime/MINLENGTH)
                        period = int(deltaTime/MINLENGTH)
                        for count in range(period):
                            noteSeq[ start + count ] = SUSTAIN 
                        noteSeq[ start ] = firstEvent.note + OFFSET
                        
                        pairFound = True
                        break;
                if not pairFound:
                    raise ValueError("Input notes can't be paired. QQ~")
                    
    return noteSeq



if __name__ == "__main__":
    mid = MidiFile("C:/Users/user/Documents/code/Music Recombination/test & learn/test1.mid")
    noteSeq = parseMIDI( mid )
    for i in noteSeq:
        print(i, end = " ")