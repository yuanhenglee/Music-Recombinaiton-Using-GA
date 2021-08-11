import numpy as np
import pandas as pd
import math


def calculateSimilarity(value, ancestors_value):
    return 1-abs(ancestors_value-value)


def calculateConsensus(mean, std, value):
    distance = math.floor(abs(mean - value)/std)
    score = (2-distance)/2
    if score > 0:
        return score
    else:
        return 0


def calculateInRange(max, min, value):
    if value <= max and value >= min:
        return 1
    return 0


def updateFitness(individual):
    ancestor = individual.ancestor
    individual.fitness = 0

    # fitness score initialize
    similarity = 0
    consensus = 0
    inRange = 0

    # similarity
    similarity_score = np.zeros(20)

    for i in range(len(similarity_score)):
        similarity_score[i] = calculateSimilarity(
            individual.features[i], ancestor.features[i])

    similarity += (similarity_score.mean())*50

    # consensus
    consensus_score = np.zeros(10)

    path_orderedData = "../test & learn/EDA Result/songMeanSTD_ordered.csv"
    path_Data = "../test & learn/EDA Result/songMeanSTD.csv"
    data = pd.read_csv(path_Data)
    orderedData = pd.read_csv(path_orderedData)
    data.rename(columns={"Unnamed: 0": "feature"}, inplace=True)
    orderedData.rename(columns={"Unnamed: 0": "feature"}, inplace=True)

    for i in range(len(consensus_score)):
        featureName = orderedData["feature"][i]
        index = data[data["feature"] == featureName].index.values[0]
        consensus_score[i] = calculateConsensus(
            data["mean"][index], data["std"][index], individual.features[index])

    consensus += (consensus_score.mean())*25

    # inRange
    inRange_score = np.zeros(20)

    for i in range(len(inRange_score)):
        inRange_score[i] = calculateInRange(
            data["max"][i], data["min"][i], individual.features[i])

    inRange += (inRange_score.mean())*25

    individual.fitness += similarity + consensus + inRange
