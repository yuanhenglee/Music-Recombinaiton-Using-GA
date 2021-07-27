import Constant as C
import Fitness as Fitness


class Individual:
    def __init__(self, _parsedMIDI, _ancestorMIDI, _cuttingPoint, _signature):
        self.parsedMIDI = _parsedMIDI
        self.ancestorMIDI = _ancestorMIDI
        self.signature = _signature
        self.cuttingPoint = _cuttingPoint

        # TODO move all melody related var into parsedMIDI ? 

        # calculate rate of rest
        totalRestDuration = 0
        for i in range(self.parsedMIDI.numberOfNotes):
            if self.parsedMIDI.noteSeq[C.PITCHINDEX][i] == 0:
                totalRestDuration += self.parsedMIDI.noteSeq[C.DURATIONINDEX][i]
        self.restRate = totalRestDuration / self.parsedMIDI.totalDuration
        # calculate density of note
        self.noteDensity = self.parsedMIDI.numberOfNotes / \
            (self.parsedMIDI.totalDuration * self.parsedMIDI.minLengthInTicks)
        # calculate range of pitch
        self.pitchRange = self.parsedMIDI.highestNote - self.parsedMIDI.lowestNote

        # calculate interval frequency ratio
        self.intervalRatios = self.calPitchRatio()

        # fitness function
        self.fitness = -1
        # Fitness.updateFitness(self)

        # ! TEST
        # self.printIndividual()


    def calPitchRatio(self):
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
        for interval in self.parsedMIDI.noteSeq[C.INTERVALINDEX]:
            if interval //7 >= 1 and interval % 7 == 0:
                intervalCount[7] += 1
            else: 
                intervalCount[interval%7] += 1
        
        intervalFreq = {}
        for k,v in intervalCount.items():
            intervalFreq[ interval2Name[k] ] = v / self.parsedMIDI.noteSeq[C.INTERVALINDEX].shape[0]

        return intervalFreq 



    def printIndividual(self):
        # OG MIDI
        # self.parsedMIDI.printMIDI()
        print("\nSignature: \n", self.signature)
        print("Rate of Rest: \n", '%.4f' % self.restRate)
        print("Density of Note: \n", '%.4f' % self.noteDensity)
        print("Range of Pitch: \n", self.pitchRange)

        print("\nFitness: \n", self.fitness)
        # segmentation info
