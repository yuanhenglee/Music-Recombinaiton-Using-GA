import numpy as np
import pandas as pd
import math
import Feature

import Constant as C


def musicSourceVariety(individual):
    sum_of_duration1 = 0
    sum_of_duration2 = 0
    sum_of_duration_mutated = 0
    for tree in individual.tree_list:
        if tree.id == C.INPUT_NAMES[0]:
            sum_of_duration1 += tree.length
        elif tree.id == C.INPUT_NAMES[1]:
            sum_of_duration2 += tree.length
        elif tree.id == "Mutated":
            sum_of_duration_mutated += tree.length
        # else:
        #     print(tree.id)
        #     print(C.INPUT_NAMES)
        #     raise ValueError("Wrong tree id")

    sum_of_duration = sum_of_duration1+sum_of_duration2
    # print(f"{sum_of_duration=}")
    # print(f"{sum_of_duration1=}")
    # print(f"{sum_of_duration2=}")
    # print(f"{sum_of_duration_mutated=}")
    result = abs(C.INPUT_RATE - sum_of_duration1/sum_of_duration)

    return result


def calculateSimilarity(value, ancestors_value):
    return abs(ancestors_value-value)


def calculateConsensus(value):
    return abs(value)


def calculateInRange(max, min, value):
    if value <= max and value >= min:
        return 0
    return 1


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
    similarity_score = np.zeros(C.NUMBER_FEATURES)

    for ancestor in ancestors:
        for i in range(len(similarity_score)):
            similarity_score[i] = calculateSimilarity(
                individual.df_features_std.iloc[0, i], ancestor.df_features_std.iloc[0, i])
        similarity += similarity_score.mean()
    similarity = similarity/len(ancestors)

    # consensus
    consensus_score = np.zeros(10)

    for i in range(len(consensus_score)):
        featureName = orderedData["feature"][i]
        index = data[data["feature"] == featureName].index.values[0]
        consensus_score[i] = calculateConsensus(
            individual.df_features_std.iloc[0, index])

    consensus += (consensus_score.mean())

    # inRange
    inRange_score = np.zeros(C.NUMBER_FEATURES)

    for i in range(len(inRange_score)):
        inRange_score[i] = calculateInRange(
            data["max"][i], data["min"][i], individual.df_features.iloc[0, i])

    inRange += (inRange_score.mean())

    # music Source Variety
    music_source_variety = musicSourceVariety(individual)

    # print("similarity: ", similarity)
    # print("consensus: ", consensus)
    # print("inRange: ", inRange)
    # print("musicCount: ", musicCount)

    individual.fitness_detail = [similarity,
                                 consensus, inRange, music_source_variety]

    total_fitness = 0
    for i in range(len(C.FITNESS_WEIGHT)):
        individual.fitness_detail[i] = C.FITNESS_WEIGHT[i] * individual.fitness_detail[i]

    individual.fitness = sum(individual.fitness_detail) 

    # print(individual.fitness_detail)
