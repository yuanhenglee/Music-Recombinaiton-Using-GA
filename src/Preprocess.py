from mido import MidiFile
from math import gcd
import numpy as np

BREAK = 0
PITCHINDEX = 0
DURATIONINDEX = 1
INTERVALINDEX = 2
RESTINDEX = 3


class ProcessedMIDI:
    OG_Mido = MidiFile()
    noteSeq = np.array([]) 
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
        self.noteSeq = np.zeros( ( 4,self.numberOfNotes) )
        curNoteIndex = 0

        for track in (self.OG_Mido.tracks):
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

                        # check if two events can possiblely be a pair
                        def isPair( a, b ):
                            if a.channel == b.channel and a.note == b.note :
                                return True;
                            return False;

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

            # add pitch interval sequence & temporary rest sequence encoding
            # by the current encoding method, same note & (note,break) are both been consider as interval = 0
            for i, curPitch in enumerate( self.noteSeq[PITCHINDEX][:-1] ):
                nextPitch = self.noteSeq[PITCHINDEX][i+1]
                if curPitch == 0 or nextPitch == 0:
                    self.noteSeq[INTERVALINDEX][i] = 0

                    # cutpoint might appear between each break
                    if curPitch == 0:
                        self.noteSeq[RESTINDEX][i] = self.noteSeq[DURATIONINDEX][i]
                    else: 
                        self.noteSeq[RESTINDEX][i] = self.noteSeq[DURATIONINDEX][i+1]

                else:
                    # TODO solve same interval with different step difference
                    self.noteSeq[INTERVALINDEX][i] = ( nextPitch  - curPitch )


    def printPeriod(self):
        print("minLengthInTicks: " + str(self.minLengthInTicks))
        print("numberOfMinLength: " + str(self.numberOfMinLength))
        print("lowestNote: " + str(self.lowestNote))
        print("highestNote: " + str(self.highestNote))

        def formattedPrint( target ):
            for i in range(self.numberOfNotes):
                print( "%3d" % ( target[i] ) , end = '')
            print("\n")
                        
        print( "Pitch Sequence:" )
        formattedPrint( self.noteSeq[PITCHINDEX] )
        print( "Duration Sequence:" )
        formattedPrint( self.noteSeq[DURATIONINDEX] )
        print( "Interval Sequence:" )
        formattedPrint( self.noteSeq[INTERVALINDEX]  )
        print( "Rest Sequence:" )
        formattedPrint( self.noteSeq[RESTINDEX] )


