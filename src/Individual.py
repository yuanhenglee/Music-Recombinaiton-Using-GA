import Constant as C
import Fitness as Fitness
import Feature as Feature
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


class Individual:
    def __init__(self, _parsedMIDI, _allElementGroups, _signature, _musicTree, _isAncestor=True, _ancestorIndividual=None):
        self.parsedMIDI = _parsedMIDI
        self.signature = _signature
        self.allElementGroups = _allElementGroups
        self.tree_list = _musicTree
        self.isAncestor = _isAncestor
        self.ancestor = [self] if _isAncestor else _ancestorIndividual
        # TODO move all melody related var into parsedMIDI ?

        # features
        self.df_features = pd.DataFrame()
        self.calculateAllFeatures()
        # TODO features need to be normalized

        # fitness function
        self.fitness = -1
        # Fitness.updateFitness(self)

        # ! TEST
        # self.details()
        # print(self.df_features)

    def calculateAllFeatures(self):
        repeatedPitchPattern = Feature.repeatedPitchPattern(self.parsedMIDI)
        repeatedRhythmPattern = Feature.repeatedRhythmPattern(self.parsedMIDI)
        features = {
            "pitchVariety": [Feature.pitchVariety(self.parsedMIDI)],
            "pitchRange": [Feature.pitchRange(self.parsedMIDI)],
            "keyCentered": [Feature.keyCentered(self.parsedMIDI)],
            "nonScaleNotes": [Feature.nonScaleNotes(self.parsedMIDI)],
            "dissonantIntervals": [Feature.dissonantIntervals(self.parsedMIDI)],
            "contourDirection": [Feature.contourDirection(self.parsedMIDI)],
            "contourStability": [Feature.contourStability(self.parsedMIDI)],
            "movementByStep": [Feature.movementByStep(self.parsedMIDI)],
            "leapReturns": [Feature.leapReturns(self.parsedMIDI)],
            "climaxStrength": [Feature.climaxStrength(self.parsedMIDI)],
            "noteDensity": [Feature.noteDensity(self.parsedMIDI)],
            "restDensity": [Feature.restDensity(self.parsedMIDI)],
            "rhythmicVariety": [Feature.rhythmicVariety(self.parsedMIDI)],
            "rhythmicRange": [Feature.rhythmicRange(self.parsedMIDI)],
            "repeatedPitchPattern2": [repeatedPitchPattern[0]],
            "repeatedRhythmPattern2": [repeatedRhythmPattern[0]],
            "repeatedPitchPattern3": [repeatedPitchPattern[1]],
            "repeatedRhythmPattern3": [repeatedRhythmPattern[1]],
            "repeatedPitchPattern4": [repeatedPitchPattern[2]],
            "repeatedRhythmPattern4": [repeatedRhythmPattern[2]],
            "leapDensity": [Feature.leapDensity(self.parsedMIDI)],
            "sumOfSquareOfInterval": [Feature.sumOfSquareOfInterval(self.parsedMIDI)]
        }

        self.df_features = pd.DataFrame(features)
        # print(self.df_features)

    def details(self):
        print("-"*30)
        if self.isAncestor:
            print("Ancestor")
        else:
            print("Offspring")
        print(f"{self.tree_list}")
        print(f"{self.fitness}")
        # self.parsedMIDI.printMIDI()
