import Constant as C
import Fitness as Fitness


class Individual:
    def __init__(self, _parsedMIDI, _ancestorMIDI, _signature):
        self.parsedMIDI = _parsedMIDI
        self.ancestorMIDI = _ancestorMIDI
        self.signature = _signature
        # calculate rate of rest
        totalRestDuration = 0
        for i in range(self.parsedMIDI.numberOfNotes):
            if self.parsedMIDI.noteSeq[C.PITCHINDEX][i] == 0:
                totalRestDuration += self.parsedMIDI.noteSeq[C.DURATIONINDEX][i]
        self.restRate = totalRestDuration / self.parsedMIDI.totalDuration
        # calculate density of note
        self.noteDensity = self.parsedMIDI.numberOfNotes / self.parsedMIDI.totalDuration
        # calculate range of pitch
        self.pitchRange = self.parsedMIDI.highestNote - self.parsedMIDI.lowestNote

        # fitness function
        self.fitness = 0
        # Fitness.updateFitness(self)

        # ! TEST
        # self.printIndividual()

    def printIndividual(self):
        # OG MIDI
        # self.parsedMIDI.printMIDI()
        print("Signature: \n", self.signature)
        print("Rate of Rest: \n", '%.4f' % self.restRate)
        print("Density of Note: \n", '%.4f' % self.noteDensity)
        print("Range of Pitch: \n", self.pitchRange)

        print("\nFitness: \n", self.fitness)
        # segmentation info
