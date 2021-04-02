from mido import MidiFile
from math import gcd
from Constant import C
import numpy as np


class ProcessedMIDI:
    OG_Mido = MidiFile()
    noteSeq = np.array([])
    tempo = 500000  # Default value
    minLengthInTicks = 0
    numberOfMinLength = 0
    numberOfNotes = 0
    lowestNote = 109
    highestNote = 20

    def __init__(self, mid, preprocess=True):
        self.OG_Mido = mid
        # self.checkMIDIValidity()

        if preprocess:
            self.exploreMIDI()
            self.parseMIDI()

    def exploreMIDI(self):
        timeSet = []  # store possible periods
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
                    self.highestNote = event.note if event.note > self.highestNote else self.highestNote

        # drop first event's delta time
        timeSet.pop(0)
        self.minLengthInTicks = gcd(*timeSet)
        self.numberOfMinLength = totalTime//self.minLengthInTicks

    def parseMIDI(self):

        # DEFINE SYMBOL FOR ENCODING
        OFFSET = 1 - self.lowestNote

        # initialize
        self.noteSeq = np.zeros((5, self.numberOfNotes))
        curNoteIndex = 0

        for track in (self.OG_Mido.tracks):
            # print('Track {}: {}'.format(i, track.name))
            for j, firstEvent in enumerate(track):

                if (firstEvent.type == "note_on"):
                    if firstEvent.time != 0 and curNoteIndex != 0 and track[j+1].time != 0:
                        duration = int(firstEvent.time/self.minLengthInTicks)
                        self.noteSeq[C.PITCHINDEX, curNoteIndex] = C.BREAK
                        self.noteSeq[C.DURATIONINDEX, curNoteIndex] = duration
                        curNoteIndex += 1
                    # find note_off event for this one
                    deltaTime = 0
                    pairFound = False
                    for secondEvent in track[j+1:-1]:
                        deltaTime += secondEvent.time

                        # check if two events can possiblely be a pair
                        def isPair(a, b):
                            if a.channel == b.channel and a.note == b.note:
                                return True
                            return False

                        if secondEvent.type == "note_off" and isPair(firstEvent, secondEvent):

                            # duration
                            duration = int(deltaTime/self.minLengthInTicks)
                            self.noteSeq[C.PITCHINDEX,
                                         curNoteIndex] = firstEvent.note + OFFSET
                            self.noteSeq[C.DURATIONINDEX,
                                         curNoteIndex] = duration
                            curNoteIndex += 1

                            pairFound = True
                            break
                    if not pairFound:
                        raise ValueError("Input notes can't be paired. QQ~")

            # add pitch interval sequence & temporary rest sequence encoding
            # by the current encoding method, same note & (note,break) are both been consider as interval = 0
            for i, curPitch in enumerate(self.noteSeq[C.PITCHINDEX][:-1]):
                nextPitch = self.noteSeq[C.PITCHINDEX][i+1]
                # cutpoint might appear between each break
                if curPitch == 0:
                    self.noteSeq[C.RESTINDEX][i] = self.noteSeq[C.DURATIONINDEX][i]
                elif nextPitch == 0 and i + 2 < self.numberOfNotes:
                    nextNextPitch = self.noteSeq[C.PITCHINDEX][i+2]
                    self.noteSeq[C.RESTINDEX][i] = self.noteSeq[C.DURATIONINDEX][i+1]
                    self.noteSeq[C.INTERVALINDEX][i]\
                        = abs(nextNextPitch - curPitch)
                    self.noteSeq[C.INTERVALINDEX][i+1]\
                        = abs(nextNextPitch - curPitch)

                else:
                    # TODO solve same interval with different step difference
                    self.noteSeq[C.INTERVALINDEX][i] = abs(
                        nextPitch - curPitch)

            # accumulative beat sequence
            for i, curDuration in enumerate(self.noteSeq[C.DURATIONINDEX][:-1]):
                self.noteSeq[C.ACCUMULATIVEINDEX][i] = curDuration
                if i != 0:
                    preDuration = self.noteSeq[C.DURATIONINDEX][i-1]
                    if self.noteSeq[C.ACCUMULATIVEINDEX][i-1] % C.BeatInMeasure != 0:
                        if preDuration < 8:
                            if self.noteSeq[C.PITCHINDEX][i-1] != 0 or preDuration <= 4:
                                self.noteSeq[C.ACCUMULATIVEINDEX][i] += self.noteSeq[C.ACCUMULATIVEINDEX][i-1]

    def printPeriod(self):
        print("minLengthInTicks: " + str(self.minLengthInTicks))
        print("numberOfMinLength: " + str(self.numberOfMinLength))
        print("lowestNote: " + str(self.lowestNote))
        print("highestNote: " + str(self.highestNote))

        def formattedPrint(target):
            for i in range(self.numberOfNotes):
                print("%3d" % (target[i]), end='')
            print("\n")

        print("Pitch Sequence:")
        formattedPrint(self.noteSeq[C.PITCHINDEX])
        print("Duration Sequence:")
        formattedPrint(self.noteSeq[C.DURATIONINDEX])
        print("Interval Sequence:")
        formattedPrint(self.noteSeq[C.INTERVALINDEX])
        print("Rest Sequence:")
        formattedPrint(self.noteSeq[C.RESTINDEX])
        print("Accumulative Beat Sequence:")
        formattedPrint(self.noteSeq[C.ACCUMULATIVEINDEX])
