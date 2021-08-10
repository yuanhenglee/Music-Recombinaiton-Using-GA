import Constant as C
import Fitness as Fitness
import Feature as Feature
import numpy as np


class Individual:
    def __init__(self, _parsedMIDI, _cuttingPoint, _signature, _isAncestor, _ancestorIndividual=None):
        self.parsedMIDI = _parsedMIDI
        self.signature = _signature
        self.cuttingPoint = _cuttingPoint
        self.isAncestor = _isAncestor
        self.ancestor = self if _isAncestor else _ancestorIndividual

        self.features = np.zeros(20)

        """ 
        self.pitchVariety = 0
        pitchRange = 1
        keyCentered = 2
        nonScaleNotes = 3
        dissonantIntervals = 4
        contourDirection = 5
        contourStability = 6
        movementByStep = 7
        leapReturns = 8
        climaxStrength = 9
        noteDensity = 10
        restDensity = 11
        rhythmicVariety = 12
        rhythmicRange = 13
        repeatedPitchPattern[0] = 14
        repeatedRhythmPattern[0] = 15
        repeatedPitchPattern[1] = 16
        repeatedRhythmPattern[1] = 17
        repeatedPitchPattern[1] = 18
        repeatedRhythmPattern[1] = 19
        """

        # TODO move all melody related var into parsedMIDI ?

        self.calculateAllFeatures()

        # fitness function
        self.fitness = -1
        Fitness.updateFitness(self)

        # ! TEST
        # self.printIndividual()

    def calculateAllFeatures(self):
        self.features[0] = Feature.pitchVariety(self.parsedMIDI)
        self.features[1] = Feature.pitchRange(self.parsedMIDI)
        self.features[2] = Feature.keyCentered(self.parsedMIDI)
        self.features[3] = Feature.nonScaleNotes(self.parsedMIDI)
        self.features[4] = Feature.dissonantIntervals(self.parsedMIDI)
        self.features[5] = Feature.contourDirection(self.parsedMIDI)
        self.features[6] = Feature.contourStability(self.parsedMIDI)
        self.features[7] = Feature.movementByStep(self.parsedMIDI)
        self.features[8] = Feature.leapReturns(self.parsedMIDI)
        self.features[9] = Feature.climaxStrength(self.parsedMIDI)
        self.features[10] = Feature.noteDensity(self.parsedMIDI)
        self.features[11] = Feature.restDensity(self.parsedMIDI)
        self.features[12] = Feature.rhythmicVariety(self.parsedMIDI)
        self.features[13] = Feature.rhythmicRange(self.parsedMIDI)
        repeatedPitchPattern = Feature.repeatedPitchPattern(self.parsedMIDI)
        repeatedRhythmPattern = Feature.repeatedRhythmPattern(self.parsedMIDI)
        self.features[14] = repeatedPitchPattern[0]
        self.features[15] = repeatedRhythmPattern[0]
        self.features[16] = repeatedPitchPattern[1]
        self.features[17] = repeatedRhythmPattern[1]
        self.features[18] = repeatedPitchPattern[2]
        self.features[19] = repeatedRhythmPattern[2]

    def printIndividual(self):
        # OG MIDI
        # self.parsedMIDI.printMIDI()
        print("\nSignature: \n", self.signature)
        print("\nCuttingPoint: \n", self.cuttingPoint)

        print("\nFitness: \n", self.fitness)
        # segmentation info
