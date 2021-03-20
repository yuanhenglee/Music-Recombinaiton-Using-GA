import os
import sys
import copy
from mido import MidiFile, Message, second2tick
from math import gcd
import numpy as np

BREAK = 0
PITCHINDEX = 0
DURATIONINDEX = 1

# check if two events can possiblely be a pair
def isPair( a, b ):
    if a.channel == b.channel and a.note == b.note :
        return True;
    return False;

class ProcessedMIDI:
    OG_Mido = MidiFile()
    noteSeq = np.array([]) # TODO
    tempo = 500000 # Default value
    minLengthInTicks = 0
    numberOfMinLength = 0
    numberOfNotes= 0
    lowestNote = 109
    highestNote = 20

    def __init__( self, mid , preprocess = True ):
        self.OG_Mido = mid
        # self.checkMIDIValidity();
        
        if preprocess:
            self.exploreMIDI()
            self.parseMIDI()

    def exploreMIDI( self ):
        timeSet = [] # store possible periods
        totalTime = 0

        for track in (self.OG_Mido.tracks):
            for j, event in enumerate(track):
                # print(event)
                if event.type == "set_tempo":
                    self.tempo = event.tempo
                elif event.type == "note_on":
                    self.numberOfNotes += 1
                    if event.time != 0 and track[j+1].time != 0:
                        self.numberOfNotes += 1

                
                if event.time > 0:
                    timeSet.append(event.time)
                    totalTime += event.time

                    self.lowestNote = event.note if event.note < self.lowestNote else self.lowestNote
                    self.highestNote = event.note if event.note >  self.highestNote else  self.highestNote

        # drop first event's delta time
        timeSet.pop(0)
        self.minLengthInTicks = gcd(*timeSet)
        self.numberOfMinLength = totalTime//self.minLengthInTicks

    def parseMIDI( self ):

        # DEFINE SYMBOL FOR ENCODING
        OFFSET = 1 - self.lowestNote

        # initialize
        self.noteSeq = np.zeros( ( 2,self.numberOfNotes) )
        curNoteIndex = 0

        for track in (mid.tracks):
            # print('Track {}: {}'.format(i, track.name))
            for j,firstEvent in enumerate(track):

                if ( firstEvent.type == "note_on" ):
                    if firstEvent.time != 0 and curNoteIndex!=0 and track[j+1].time != 0:
                        duration = int(firstEvent.time/self.minLengthInTicks)
                        self.noteSeq[PITCHINDEX,curNoteIndex] = BREAK
                        self.noteSeq[DURATIONINDEX,curNoteIndex] = duration
                        curNoteIndex += 1
                    # find note_off event for this one
                    deltaTime = 0
                    pairFound = False
                    for secondEvent in track[j+1:-1]:
                        deltaTime += secondEvent.time;
                        if secondEvent.type == "note_off" and isPair (firstEvent,secondEvent):

                            # duration
                            duration = int(deltaTime/self.minLengthInTicks)
                            self.noteSeq[PITCHINDEX,curNoteIndex] = firstEvent.note + OFFSET
                            self.noteSeq[DURATIONINDEX,curNoteIndex] = duration
                            curNoteIndex += 1

                            pairFound = True
                            break;
                    if not pairFound:
                        raise ValueError("Input notes can't be paired. QQ~")

    def printPeriod(self):
        print("minLengthInTicks: " + str(self.minLengthInTicks))
        print("numberOfMinLength: " + str(self.numberOfMinLength))
        print("lowestNote: " + str(self.lowestNote))
        print("highestNote: " + str(self.highestNote))
        print("noteSeq: ")
        print(self.noteSeq)

def LBDM( target ):
    # DEFINE ICR PR DURATION WEIGHT
    ICR = 1
    PR = 1

    seqTable = copy.deepcopy( target.noteSeq )
    seqTable = np.vstack( ( seqTable , np.zeros( (9,target.numberOfNotes) ) ) )

    # TODO pack this into a function
    # input: target sequence
    # output: generated weight

    # ICR + PR + duration 
    for i, previousDuration in enumerate( seqTable[DURATIONINDEX][:-1] ):
        currentDuration = seqTable[DURATIONINDEX][i+1]
        PIncrement = 0
        CIncrement = 0
        if previousDuration != currentDuration: 
            CIncrement += ICR
            PIncrement += ICR
        if previousDuration < currentDuration: 
            CIncrement += PR
        if previousDuration > currentDuration: 
            PIncrement += PR

        ## find true duration including break
        fixedDuration = previousDuration
        if seqTable[PITCHINDEX][i] == 0 and i > 1:
            fixedDuration = previousDuration + seqTable[DURATIONINDEX][i-1]
        if fixedDuration != currentDuration:
            PIncrement += 2

        seqTable[DURATIONINDEX + 1][i] += PIncrement
        seqTable[DURATIONINDEX + 1][i+1] += CIncrement
    






    # seqTable = np.append( seqTable , )
    print( seqTable )



if __name__ == "__main__":

        mid = MidiFile("C:/Users/user/Documents/code/Music Recombination/midi_file/young.mid")

        period = ProcessedMIDI( mid)

        period.printPeriod()

        LBDM( period )