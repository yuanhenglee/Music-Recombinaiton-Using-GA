from hashlib import new
import sys
import os
import time
from mido import MidiFile
from Feature import main
import Preprocess
import MusicSegmentation_2
from Individual import Individual
from Fitness import updateFitness
from ILBDM import ILBDM, ILBDM_elementary_noteSeq
import Utility
import Constant as C

import numpy as np
import random
from zodb import ZODB, transaction
import copy
import Demo
import MusicTree


def startGA(initialAncestors, population, mutation_rate=0.1, crossover_rate=0.3, max_generation=1000, max_population=1000, n_generation_terminate=100, generation_to_kill=10):
    best_score = 99999999999
    generation_best_score_was_born = 1
    for generation in range(1, max_generation+1):
        # Measuring the fitness of each chromosome in the population.
        for individual in population:
            updateFitness(individual)

        if generation >= generation_to_kill and len(population) > max_population:
            population.sort(key=lambda x: x.fitness)
            tmp_population = []
            key_fitness = 0
            for individual in population:
                if individual.fitness != key_fitness:
                    key_fitness = individual.fitness
                    tmp_population.append(individual)
            population = tmp_population

        population = natural_selection(population, max_population)

        for i in population:
            if i.isAncestor != True:
                if i.fitness < best_score:
                    best_score = i.fitness
                    generation_best_score_was_born = generation
                break

        # ! TEST ONLY
        print("==================\ngeneration: \n", generation)

        for individual in population:
            if individual.isAncestor == True:
                print("*", end="")
            else:
                print(" ", end="")
            if np.isnan(individual.fitness):
                print(individual.tree_list[0].id)
                quit()

            print(round(individual.fitness, 6))
        # print("\n", population[0].parsedMIDI.noteSeq[C.INTERVALINDEX])
        # ! TEST ONLY

        ''' terminate '''
        if population[0] == 0 or generation - generation_best_score_was_born >= n_generation_terminate:
            print("GA Terminate")
            break

        ''' Generating next generation using crossover. '''
        population += crossover(population, initialAncestors,
                                n_offspring=crossover_rate * max_population)

        # TODO control how many individuals will be mutated
        ''' Adding some variations to the offspring using mutation. '''
        population += mutation(population, initialAncestors,
                               int(mutation_rate * max_population))

    return population


def natural_selection(population, n_selected_goal):
    ''' Selecting the best individuals in the current generation for the next generation. '''
    if len(population) <= n_selected_goal:
        return population
    else:
        population.sort(key=lambda x: x.fitness)
        ancestors = []
        for i in population[n_selected_goal:]:
            if i.isAncestor:
                ancestors.append(i)
        return population[0:n_selected_goal] + ancestors


def crossover(parents, initialAncestors, n_offspring):
    offspring = []
    n_times_trying = 0
    # stop when offspring size satisfies the criteria or either the n_times_trying exceed
    while len(offspring) < n_offspring and n_times_trying < 100:
        main_parent, sub_parent = random.choices(parents, k=2)
        n_times_trying += 1
        if main_parent == sub_parent:
            continue

        ''' Crossover '''
        # crossover
        # find elements to be crossovered
        point, id = selectRandomElement(main_parent)
        # construct offspring based on main_parent
        child = copy.deepcopy(main_parent)
        child.isAncestor = False
        child.ancestor = initialAncestors

        # find suitable sequence for filler
        blank_length = int(
            sum(main_parent.parsedMIDI.noteSeq[C.DURATIONINDEX][point[0][0]:point[0][1]]))
        # print("blank length: ", blank_length)
        filler_trees = MusicTree.findSolutionForBlank(
            blank_length, sub_parent.tree_list)

        # case where filling fail
        if filler_trees == None:
            continue
        # print(f"{filler_trees=}")
        np.random.seed(int(time.time()))
        rand_value = np.random.rand()
        new_num = hash((rand_value, main_parent.signature, "crossover"))
        for tree in filler_trees:
            for i in range(len(tree.elementary_noteSeq[2])):
                tree.elementary_noteSeq[2][i] = new_num

        # filling the blank

        # for each tree containing a gap, split it into subtrees where the gap been a independent tree
        gaps_in_tree_index = []
        for gap in point:
            acc_tree_index = 0
            for i, tree in enumerate(child.tree_list):
                if acc_tree_index <= gap[0] and gap[1] <= acc_tree_index + len(tree.pitchSeq):
                    split_trees, gap_index_split_trees = tree.splitToThree(
                        gap[0]-acc_tree_index, gap[1]-acc_tree_index)
                    if i+1 < len(child.tree_list):
                        child.tree_list = child.tree_list[:i] + \
                            split_trees + child.tree_list[i+1:]
                    else:
                        child.tree_list = child.tree_list[:i] + split_trees
                    gaps_in_tree_index.append(i+gap_index_split_trees)
                acc_tree_index += len(tree.pitchSeq)

        # replace each gap tree
        tmp_tree_list = []
        for t in range(len(child.tree_list)):
            if t in gaps_in_tree_index:
                # print("replacing ", child.tree_list[t], " with ", filler_trees)
                tmp_tree_list += filler_trees
            else:
                tmp_tree_list.append(child.tree_list[t])
        child.tree_list = tmp_tree_list

        # print(child.tree_list)

        # construct noteSeq for child
        tmp_elementary_noteSeq = np.array([[], [], []])
        for tree in child.tree_list:
            tmp_elementary_noteSeq = np.hstack(
                [tmp_elementary_noteSeq, tree.elementary_noteSeq])
        tmp_element_number_list = copy.deepcopy(tmp_elementary_noteSeq[2])
        child.parsedMIDI.noteSeq = Preprocess.expandElementarySequence(
            tmp_elementary_noteSeq)
        # update element number list
        child.parsedMIDI.noteSeq[C.ELEMENTINDEX] = tmp_element_number_list
        child.allElementGroups = set(tmp_element_number_list)
        if child.signature not in child.allElementGroups:
            print("main_parent signature: \n", main_parent.signature)
            print("child signature: \n", child.signature)
            print("main_parent group: \n", main_parent.allElementGroups)
            print("child group: \n", child.allElementGroups)
            print("Error in crossover")
        # print(child.parsedMIDI.noteSeq[C.ELEMENTINDEX])
        child.parsedMIDI.updateFieldVariable()
        child.calculateAllFeatures()

        # main_parent.details()
        # child.details()

        offspring.append(child)
    offspring.sort(key=lambda x: x.fitness, reverse=True)
    return offspring

# TODO preserve the original individual


def mutation(parents, initialAncestors, mutation_size):
    newPopulation = []

    selected_parents = random.sample(parents, mutation_size)

    for main_parent in selected_parents:

        child = copy.deepcopy(main_parent)
        child.isAncestor = False
        child.ancestor = initialAncestors

        point, id = selectRandomElement(child)

        if bool(random.getrandbits(1)):
            for (start, end) in point:
                pitchShifting(start, end, child, id)
        else:
            for (start, end) in point:
                pitchOrderReverse(start, end, child, id)

        child.parsedMIDI.updateFieldVariable(child.parsedMIDI)
        child.calculateAllFeatures()
        # print(child.parsedMIDI.noteSeq[C.ELEMENTINDEX])
        newPopulation.append(child)

    return newPopulation


def pitchOrderReverse(start, end, target, id):
    # Pitch
    target.parsedMIDI.noteSeq[C.PITCHINDEX][start:end] = np.flipud(
        target.parsedMIDI.noteSeq[C.PITCHINDEX][start:end])
    # Duration
    target.parsedMIDI.noteSeq[C.DURATIONINDEX][start:end] = np.flipud(
        target.parsedMIDI.noteSeq[C.DURATIONINDEX][start:end])
    # Rest
    target.parsedMIDI.noteSeq[C.RESTINDEX][start:end] = np.flipud(
        target.parsedMIDI.noteSeq[C.RESTINDEX][start:end])
    # Interval

    def calculateInterval(i):
        if i < 0 or i >= target.parsedMIDI.numberOfNotes-1:
            return
        if target.parsedMIDI.noteSeq[C.PITCHINDEX][i+1] == 0:
            if i + 2 < target.parsedMIDI.numberOfNotes:
                nextNextPitch = target.parsedMIDI.noteSeq[C.PITCHINDEX][i+2]
                target.parsedMIDI.noteSeq[C.INTERVALINDEX][i]\
                    = abs(nextNextPitch - target.parsedMIDI.noteSeq[C.PITCHINDEX][i])
                target.parsedMIDI.noteSeq[C.INTERVALINDEX][i+1]\
                    = abs(nextNextPitch - target.parsedMIDI.noteSeq[C.PITCHINDEX][i])
            else:
                target.parsedMIDI.noteSeq[C.INTERVALINDEX][i] = 0
        else:
            target.parsedMIDI.noteSeq[C.INTERVALINDEX][i]\
                = abs(target.parsedMIDI.noteSeq[C.PITCHINDEX][i+1] - target.parsedMIDI.noteSeq[C.PITCHINDEX][i])
    for i in range(start-2, end + 2):
        calculateInterval(i)

    # Element
    np.random.seed(int(time.time()))
    rand_value = np.random.rand()
    # new_num = hash(("mutation", target.signature, rand_value))
    new_num = hash((rand_value, target.signature, "mutation"))
    newElementSeq = [new_num]*(end-start)
    target.parsedMIDI.noteSeq[C.ELEMENTINDEX][start:end] = newElementSeq
    target.allElementGroups = set(target.parsedMIDI.noteSeq[C.ELEMENTINDEX])
    if target.signature not in target.allElementGroups:
        print("Error in reverse")

    newElementarySeq = np.vstack(
        [target.parsedMIDI.noteSeq[C.PITCHINDEX][start:end],
         target.parsedMIDI.noteSeq[C.DURATIONINDEX][start:end], newElementSeq])
    mutateTree(start, end, target, newElementarySeq, id)


def pitchShifting(start, end, target, id):
    move = random.randint(1, 4)
    negative = random.randint(0, 1)
    if negative == 1:
        move = move * -1
    newPitchSeq = []
    for i in range(start, end):
        if target.parsedMIDI.noteSeq[C.PITCHINDEX][i] != 0:
            newPitch = target.parsedMIDI.noteSeq[C.PITCHINDEX][i] + move
            if Utility.isValidPitch(newPitch):
                newPitchSeq.append(newPitch)
            else:
                return
        else:
            newPitchSeq.append(0)
    # noteSeq mutation

    np.random.seed(int(time.time()))
    rand_value = np.random.rand()
    new_num = hash((rand_value, target.signature, "mutation"))
    newElementSeq = [new_num]*(end-start)
    target.parsedMIDI.noteSeq[C.PITCHINDEX][start:end] = newPitchSeq
    target.parsedMIDI.noteSeq[C.ELEMENTINDEX][start:end] = newElementSeq
    target.allElementGroups = set(target.parsedMIDI.noteSeq[C.ELEMENTINDEX])
    if target.signature not in target.allElementGroups:
        print("Error in shifting")
    newElementarySeq = np.vstack(
        [newPitchSeq, target.parsedMIDI.noteSeq[C.DURATIONINDEX][start:end], newElementSeq])
    mutateTree(start, end, target, newElementarySeq, id)


def mutateTree(start, end, target, newElementarySeq, id):
    # tree mutation
    fillerTree = MusicTree.treeNode(
        id, 0,
        newElementarySeq[0],
        newElementarySeq[1],
        newElementarySeq[2],
        ILBDM_elementary_noteSeq(newElementarySeq))
    gaps_in_tree_index = []
    acc_tree_index = 0
    for i, tree in enumerate(target.tree_list):
        if acc_tree_index <= start and end <= acc_tree_index + len(tree.pitchSeq):
            split_trees, gap_index_split_trees = tree.splitToThree(
                start-acc_tree_index, end-acc_tree_index)
            if i+1 < len(target.tree_list):
                target.tree_list = target.tree_list[:i] + \
                    split_trees + target.tree_list[i+1:]
            else:
                target.tree_list = target.tree_list[:i] + split_trees
            gaps_in_tree_index.append(i+gap_index_split_trees)
        acc_tree_index += len(tree.pitchSeq)

    # replace each gap tree
    tmp_tree_list = []
    for t in range(len(target.tree_list)):
        if t in gaps_in_tree_index:
            tmp_tree_list += [fillerTree]
        else:
            tmp_tree_list.append(target.tree_list[t])
    target.tree_list = tmp_tree_list


def findBestOffspring(population):
    population.sort(key=lambda x: x.fitness)
    for i in population:
        if i.isAncestor != True:
            return i
    return None


def selectRandomElement(individual):
    # selected element can not be signature
    element_number_set = copy.deepcopy(individual.allElementGroups)
    element_number_set.remove(individual.signature)
    selected_element_number = random.sample(element_number_set, 1)[0]
    point = []
    tree_sublist = []
    start = -1
    element_number_list = individual.parsedMIDI.noteSeq[C.ELEMENTINDEX]
    for i, number in enumerate(element_number_list):
        if number == selected_element_number and start == -1:
            start = i
        elif number != selected_element_number and start != -1:
            end = i
            point.append((start, end))
            start = -1
        if start != -1 and i == len(element_number_list)-1:
            end = i+1
            point.append((start, end))

    # finding tree been select
    acc_tree_index = 0
    duration_before = sum(
        [i for i in individual.parsedMIDI.noteSeq[C.DURATIONINDEX][:point[0][0]]])
    duration_after = sum(
        [i for i in individual.parsedMIDI.noteSeq[C.DURATIONINDEX][:point[0][1]]])

    for tree in individual.tree_list:
        acc_tree_index += tree.length
        if(tree_sublist == [] and duration_before < acc_tree_index):
            tree_sublist.append(tree)
        if(duration_before <= acc_tree_index <= duration_after):
            tree_sublist.append(tree)

    if len(tree_sublist) == 1:
        selected_id = tree_sublist[0].id
    else:
        if tree_sublist[0].id == tree_sublist[1].id:
            selected_id = tree_sublist[0].id
        else:
            selected_id = "Mutated"

    return point, selected_id


if __name__ == "__main__":

    try:
        paths = sys.argv[1:3]
    except:
        print("Missing input MIDI file!")

    try:
        rate = sys.argv[3]
    except:
        rate = 0.5
    population = []
    initialAncestors = []

    for path in paths:
        db = ZODB(path)
        dbroot = db.dbroot
        initialAncestors.append(dbroot[0])
        for key in dbroot.keys():
            population.append(dbroot[key])
        db.close()
        string_list = path.split("/")
        name = string_list[-1]
        C.INPUT_NAMES.append(name[:-3])
    C.INPUT_RATE = float(rate)
    # print(ids)
    new_population = startGA(initialAncestors, population,
                             max_population=30, max_generation=1000)
    bestOffspring = findBestOffspring(new_population)
    # bestOffspring = population[0]

    if bestOffspring != None:
        bestOffspring.parsedMIDI.printMIDI()
        mid_output = Demo.parsed2MIDI(bestOffspring.parsedMIDI)
        cur_time = str(time.strftime('%m_%d_%H_%M', time.localtime()))
        mid_output.save('../output/' + cur_time + ".mid")
        os.makedirs("../output/" + cur_time)
        dbpath = "../output/" + cur_time + "/" + cur_time + ".fs"
        db = ZODB(dbpath)
        db.dbroot["Individual"] = bestOffspring
        transaction.commit()
        db.close()
