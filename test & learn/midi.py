from mido import MidiFile, Message, second2tick
from math import gcd
import numpy as np

# check if two events can possiblely be a pair


def isPair(a, b):
    if a.channel == b.channel and a.note == b.note:
        return True
    return False


class notesPeriod:
    OG_Mido = MidiFile()
    noteSeq = np.array([])
    totalLength = 0
    minLength = 0
    maxNote = 0
    lowest = 109
    highest = 20

    def __init__(self, mid, preprocess=True):
        self.OG_Mido = mid
        if preprocess:
            self.exploreMIDI()
            # self.parseMIDI()

    def exploreMIDI(self):

        timeSet = []  # store possible periods
        totalTime = 0
        tempo = 500000  # Default value

        for i, track in enumerate(self.OG_Mido.tracks):
            for j, event in enumerate(track):
                print(event)
                if event.type == "set_tempo":
                    tempo = event.tempo
                if event.time > 0:
                    timeSet.append(event.time)
                    totalTime += event.time

                    # self.lowest = event.note if event.note < self.lowest else self.lowest
                    # self.highest = event.note if event.note > self.highest else self.highest

        # drop first event's delta time
        timeSet.pop(0)
        self.minLength = gcd(*timeSet)
        self.maxNote = totalTime//self.minLength
        self.totalLength = second2tick(
            self.OG_Mido.length, self.OG_Mido.ticks_per_beat, tempo)

    def printPeriod(self):
        print("totalLength: " + str(self.totalLength))
        print("minLength: " + str(self.minLength))
        print("maxNote: " + str(self.maxNote))
        print("lowest: " + str(self.lowest))
        print("highest: " + str(self.highest))
        print("noteSeq: ")
        for i in self.noteSeq:
            print(i, end=" ")

    def parseMIDI(self):

        # DEFINE SYMBOL FOR ENCODING
        OFFSET = 1 - self.lowest
        BREAK = 0
        SUSTAIN = self.highest + OFFSET + 1

        # initialize
        self.noteSeq = np.full(self.maxNote, BREAK)
        curTime = -1  # will be 0 when we find the first ON event

        for i, track in enumerate(mid.tracks):
            print('Track {}: {}'.format(i, track.name))
            for j, firstEvent in enumerate(track):

                if firstEvent.type == "note_on" and curTime == -1:
                    curTime = 0  # first note-on
                else:
                    curTime += firstEvent.time

                if (firstEvent.type == "note_on"):
                    # find note_off event for this one
                    deltaTime = 0
                    pairFound = False
                    for secondEvent in track[j+1:-1]:
                        deltaTime = deltaTime + secondEvent.time
                        if secondEvent.type == "note_off" and isPair(firstEvent, secondEvent):

                            # test
                            # print(firstEvent)
                            # print(secondEvent)
                            # print("delta time = " + str(deltaTime) )
                            # print("current Time = " + str(curTime) + "\n---\n" )
                            # test

                            start = int(curTime/self.minLength)
                            duration = int(deltaTime/self.minLength)
                            for count in range(duration):
                                self.noteSeq[start + count] = SUSTAIN
                            self.noteSeq[start] = firstEvent.note + OFFSET

                            pairFound = True
                            break
                    if not pairFound:
                        raise ValueError("Input notes can't be paired. QQ~")


if __name__ == "__main__":
    mid = MidiFile("./midi_file/刻在我心底的名字.mid")

    period = notesPeriod(mid)

    period.printPeriod()
