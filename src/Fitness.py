import numpy as np
import pandas as pd
import math

from Feature import musicCounter


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
    ancestors = individual.ancestor
    individual.fitness = 0

    # fitness score initialize
    similarity = 0
    consensus = 0
    inRange = 0

    path_orderedData = "../test & learn/EDA Result/songMeanSTD_ordered.csv"
    path_Data = "../test & learn/EDA Result/songMeanSTD.csv"
    data = pd.read_csv(path_Data)
    orderedData = pd.read_csv(path_orderedData)
    data.rename(columns={"Unnamed: 0": "feature"}, inplace=True)
    orderedData.rename(columns={"Unnamed: 0": "feature"}, inplace=True)

    # similarity
    similarity_score = np.zeros(22)

    for ancestor in ancestors:
        for i in range(len(similarity_score)):
            similarity_score[i] = calculateSimilarity(
                individual.df_features.iloc[0, i], ancestor.df_features.iloc[0, i])
        similarity += similarity_score.mean()
    similarity = similarity/len(ancestors)*50

    # consensus
    consensus_score = np.zeros(10)

    for i in range(len(consensus_score)):
        featureName = orderedData["feature"][i]
        index = data[data["feature"] == featureName].index.values[0]
        consensus_score[i] = calculateConsensus(
            data["mean"][index], data["std"][index], individual.df_features.iloc[0, index])

    consensus += (consensus_score.mean())*25

    # inRange
    inRange_score = np.zeros(22)

    for i in range(len(inRange_score)):
        inRange_score[i] = calculateInRange(
            data["max"][i], data["min"][i], individual.df_features.iloc[0, i])

    inRange += (inRange_score.mean())*25

    # music Count
    musicCount = musicCounter(individual.tree_list)
    print("similarity: ", similarity)
    print("consensus: ", consensus)
    print("inRange: ", inRange)
    print("musicCount: ", musicCount)

    individual.fitness += (similarity + consensus + inRange) * musicCount
