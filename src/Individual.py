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
        self.df_features_std = pd.DataFrame()
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
            "Pitch Variety": [Feature.pitchVariety(self.parsedMIDI)],
            "Pitch Range": [Feature.pitchRange(self.parsedMIDI)],
            "Key Centered": [Feature.keyCentered(self.parsedMIDI)],
            "Non-scale Notes": [Feature.nonScaleNotes(self.parsedMIDI)],
            "Dissonant Intervals": [Feature.dissonantIntervals(self.parsedMIDI)],
            "Contour Direction": [Feature.contourDirection(self.parsedMIDI)],
            "Contour Stability": [Feature.contourStability(self.parsedMIDI)],
            "Movement By Step": [Feature.movementByStep(self.parsedMIDI)],
            "Leap Returns": [Feature.leapReturns(self.parsedMIDI)],
            "Climax Strength": [Feature.climaxStrength(self.parsedMIDI)],
            "Note Density": [Feature.noteDensity(self.parsedMIDI)],
            "Rest Density": [Feature.restDensity(self.parsedMIDI)],
            "Rhythmic Variety": [Feature.rhythmicVariety(self.parsedMIDI)],
            "Rhythmic Range": [Feature.rhythmicRange(self.parsedMIDI)],
            "Repeated Pitch_2": [repeatedPitchPattern[0]],
            "Repeated Rhythm_2": [repeatedRhythmPattern[0]],
            "Repeated Pitch_3": [repeatedPitchPattern[1]],
            "Repeated Rhythm_3": [repeatedRhythmPattern[1]],
            "Repeated Pitch_4": [repeatedPitchPattern[2]],
            "Repeated Rhythm_4": [repeatedRhythmPattern[2]],
            "LeapDensity": [Feature.leapDensity(self.parsedMIDI)],
            "SumOfSquareOfInterval": [Feature.sumOfSquareOfInterval(self.parsedMIDI)]
        }

        self.df_features = pd.DataFrame(features)
        self.df_features_std = Feature.standardization(self.df_features)
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
