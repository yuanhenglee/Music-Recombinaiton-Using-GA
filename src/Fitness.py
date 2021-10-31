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


def calculateLongNote(individual):
    long_note_score = []
    parsedMIDI = individual.parsedMIDI
    valid_note_1 = [1.0, 2.0, 3.0]
    valid_note_2 = [7.0, 6.0, 5.0]
    for i in range(parsedMIDI.numberOfNotes):
        if parsedMIDI.noteSeq[C.DURATIONINDEX][i] > max(4, np.percentile(parsedMIDI.noteSeq[C.DURATIONINDEX], 75)):
            pitch = (float(parsedMIDI.noteSeq[C.PITCHINDEX][i] % 7))
            if pitch in valid_note_1:
                long_note_score.append(0)
            elif pitch in valid_note_2:
                long_note_score.append(1)
            else:
                long_note_score.append(5)
    if len(long_note_score) > 0:
        long_note_score = np.mean(long_note_score)
    else:
        long_note_score = 0

    return long_note_score


def calculateInRange(max, min, value):
    if value <= max and value >= min:
        return 0
    return 1


def elementsTransition(individual):
    first_note = individual.tree_list[0].pitchSeq[-1]
    if first_note == 0 and len(individual.tree_list[0].pitchSeq) > 1:
        first_note = individual.tree_list[0].pitchSeq[-2]
    each_score = []
    for tree in individual.tree_list[1:]:
        second_note = tree.pitchSeq[0]
        if second_note == 0 and len(tree.pitchSeq) > 1:
            second_note = tree.pitchSeq[1]
        interval = abs(second_note - first_note)
        if first_note == 0 or second_note == 0:
            interval = 0.0
        if interval in [0.0, 1.0, 2.0]:
            each_score.append(0)
        elif interval in [3.0, 4.0]:
            each_score.append(1)
        elif interval in [5.0, 6.0, 7.0]:
            each_score.append(10)
        else:
            each_score.append(20)
        first_note = tree.pitchSeq[-1]
        if first_note == 0 and len(tree.pitchSeq) > 1:
            first_note = tree.pitchSeq[-2]

        # print(tree.pitchSeq)
        # print(interval)

    if len(each_score) > 0:
        return np.mean(each_score)
    else:
        return 0


def tailScore(individual):
    last_pitch = individual.parsedMIDI.noteSeq[C.PITCHINDEX][-1]
    last_duration = individual.parsedMIDI.noteSeq[C.DURATIONINDEX][-1]
    last_2_pitch = individual.parsedMIDI.noteSeq[C.PITCHINDEX][-2]
    if last_pitch == 0:
        last_pitch = individual.parsedMIDI.noteSeq[C.PITCHINDEX][-2]
        last_duration = individual.parsedMIDI.noteSeq[C.DURATIONINDEX][-2]
        last_2_pitch = individual.parsedMIDI.noteSeq[C.PITCHINDEX][-3]

    if float(last_pitch) % 7 in [1.0]:
        score_last_pitch = 0
    elif float(last_pitch) % 7 in [2.0, 5.0, 6.0]:
        score_last_pitch = 1
    else:
        score_last_pitch = 5

    duration_ratio = float(last_duration) / \
        np.mean(individual.parsedMIDI.noteSeq[C.DURATIONINDEX])
    if duration_ratio >= 2:
        score_last_duration = 0
    elif duration_ratio >= 1:
        score_last_duration = 1
    else:
        score_last_duration = 5

    interval = abs(last_pitch - last_2_pitch)
    if interval in [0.0, 1.0, 2.0]:
        score_interval = 0
    else:
        score_interval = 5

    return score_last_pitch + score_last_duration + score_interval


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
        df_tmp = C.similarity_weight * \
            (ancestor.df_features_std - individual.df_features_std)
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
    consensus += 3 * elementsTransition(individual)
    consensus += calculateLongNote(individual)
    consensus += tailScore(individual)

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

    # n_tree = len(individual.tree_list)
    # if 10 <= n_tree <= 16:
    #     n_tree_score = 0
    # elif 10 > n_tree:
    #     n_tree_score = abs(n_tree - 10)
    # elif n_tree > 16:
    #     n_tree_score = abs(n_tree - 16)

    # n tree score
    n_invalid_tree = 0
    for tree in individual.tree_list:
        if 1/16 <= tree.length/individual.parsedMIDI.totalDuration:  # <= 1/10:
            ...
        else:
            n_invalid_tree += 1
    n_tree_score = n_invalid_tree/len(individual.tree_list)

    # element alternate rate
    n_element_alternate = 0
    if len(individual.tree_list) <= 1:
        element_alternate_score = 1
    else:
        cur_tree_id = individual.tree_list[0].id
        for tree in individual.tree_list:
            if tree.id != cur_tree_id:
                n_element_alternate += 1
                cur_tree_id = tree.id
        element_alternate_score = 1 - n_element_alternate / \
            (len(individual.tree_list)-1)

    individual.fitness_detail = [similarity,
                                 consensus, inRange, music_source_variety, n_tree_score, element_alternate_score]

    for i in range(len(C.FITNESS_WEIGHT)):
        individual.fitness_detail[i] = C.FITNESS_WEIGHT[i] * \
            individual.fitness_detail[i]

    individual.fitness = sum(individual.fitness_detail)

    # print(individual.fitness_detail)
