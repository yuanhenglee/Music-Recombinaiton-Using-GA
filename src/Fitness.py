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
    if sum_of_duration == 0:
        return 1
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

def elementsTransition( individual ):
    first_note = individual.tree_list[0].pitchSeq[-1]
    each_score = []
    for tree in individual.tree_list[1:]:
        second_note = tree.pitchSeq[0]
        interval = abs(second_note - first_note)
        if interval in [0.0, 1.0, 2.0]:
            each_score.append(0)
        elif interval in [3.0, 4.0]:
            each_score.append(1)
        elif interval in [5.0, 6.0, 7.0]:
            each_score.append(2)
        else:
            each_score.append(5)
        first_note = tree.pitchSeq[-1]
    if len(each_score) > 0:
        return np.mean(each_score)
    else:
        return 0



def updateFitness(individual):
    individual.fitness = 0

    # fitness score initialize
    similarity = 0
    consensus = 0
    inRange = 0

    # path_orderedData = "../test & learn/EDA Result/songMeanSTD_ordered.csv"
    path_Data = "../test & learn/EDA Result/songMeanSTD.csv"
    data = pd.read_csv(path_Data)
    # orderedData = pd.read_csv(path_orderedData)
    # data.rename(columns={"Unnamed: 0": "feature"}, inplace=True)
    # orderedData.rename(columns={"Unnamed: 0": "feature"}, inplace=True)

    # similarity
    similarity = 0
    for ancestor in individual.ancestor:
        df_tmp = C.similarity_weight * (ancestor.df_features_std - individual.df_features_std)
        similarity += df_tmp.abs().to_numpy().sum()
    # similarity_score = np.zeros(C.NUMBER_FEATURES)

    # for ancestor in ancestors:
    #     for i in range(len(similarity_score)):
    #         similarity_score[i] = calculateSimilarity(
    #             individual.df_features_std.iloc[0, i], ancestor.df_features_std.iloc[0, i])
    #     similarity += similarity_score.mean()
    # similarity = similarity/len(ancestors)

    # consensus
    df_consensus_score = C.consensus_weight * individual.df_features_std
    consensus = df_consensus_score.abs().to_numpy().sum()
    consensus += elementsTransition(individual) 
    

        # consensus_score = np.zeros(10)

        # for i in range(len(consensus_score)):
        #     featureName = orderedData["feature"][i]
        #     index = data[data["feature"] == featureName].index.values[0]
        #     consensus_score[i] = calculateConsensus(
        #         individual.df_features_std.iloc[0, index])

        # consensus += (consensus_score.mean())

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

    n_tree = len(individual.tree_list)
    if 10<=n_tree<=16:
        n_tree_score = 0
    elif 10>n_tree:
        n_tree_score = abs(n_tree - 10)
    elif n_tree>16:
        n_tree_score = abs(n_tree - 16)
    

    individual.fitness_detail = [similarity,
                                 consensus, inRange, music_source_variety, n_tree_score]

    for i in range(len(C.FITNESS_WEIGHT)):
        individual.fitness_detail[i] = C.FITNESS_WEIGHT[i] * \
            individual.fitness_detail[i]

    individual.fitness = sum(individual.fitness_detail)

    # print(individual.fitness_detail)

    
