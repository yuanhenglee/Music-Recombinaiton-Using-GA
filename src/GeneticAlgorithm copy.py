from hashlib import new
import sys
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


def startGA(initialAncestors, population, mutation_rate=0.3, crossover_rate=0.3, max_generation=1000, max_population=1000, n_generation_terminate=100, generation_to_kill=10):
    best_score = 0
    generation_best_score_was_born = 1
    for generation in range(1, max_generation+1):
        # Measuring the fitness of each chromosome in the population.
        for individual in population:
            updateFitness(individual)

        if generation >= generation_to_kill and len(population) > max_population:
            population.sort(key=lambda x: x.fitness, reverse=True)
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
                if i.fitness > best_score:
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
            print(round(individual.fitness, 6))
        # print("\n", population[0].parsedMIDI.noteSeq[C.INTERVALINDEX])
        # ! TEST ONLY

        ''' terminate '''
        if population[0] == 100 or generation - generation_best_score_was_born >= n_generation_terminate:
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


def natural_selection(population, n_selected):
    ''' Selecting the best individuals in the current generation for the next generation. '''
    if len(population) <= n_selected:
        return population
    else:
        population.sort(key=lambda x: x.fitness, reverse=True)
        return population[0:n_selected]


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
        point = selectRandomElement(main_parent)
        # construct offspring based on main_parent
        child = copy.deepcopy(main_parent)
        child.isAncestor = False
        child.ancestor = initialAncestors

        # find suitable sequence for filler
        blank_length = int(
            sum(main_parent.parsedMIDI.noteSeq[C.DURATIONINDEX][point[0][0]:(point[0][1])]))
        # print("blank length: ", blank_length)
        filler_trees = MusicTree.findSolutionForBlank(
            blank_length, sub_parent.tree_list)

        # case where filling fail
        if filler_trees == None:
            continue
        # print(f"{filler_trees=}")
        rand_value = random.seed()
        new_num = hash(("crossover", main_parent.signature, rand_value))
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
        tmp_element_number_list = tmp_elementary_noteSeq[2].copy()
        child.parsedMIDI.noteSeq = Preprocess.expandElementarySequence(
            tmp_elementary_noteSeq)
        # update element number list
        child.parsedMIDI.noteSeq[C.ELEMENTINDEX] = tmp_element_number_list
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

        point = selectRandomElement(child)

        if bool(random.getrandbits(1)):
            for (start, end) in point:
                pitchShifting(start, end, child)
        else:
            for (start, end) in point:
                pitchOrderReverse(start, end, child)

        child.parsedMIDI.updateFieldVariable(child.parsedMIDI)
        child.calculateAllFeatures()
        # print(child.parsedMIDI.noteSeq[C.ELEMENTINDEX])
        newPopulation.append(child)

    return newPopulation


def pitchOrderReverse(start, end, target):
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
    rand_value = random.seed()
    new_num = hash(("mutation", target.signature, rand_value))
    newElementSeq = [new_num]*(end-start)
    target.parsedMIDI.noteSeq[C.ELEMENTINDEX][start:end] = newElementSeq

    newElementarySeq = np.vstack(
        [target.parsedMIDI.noteSeq[C.PITCHINDEX][start:end],
         target.parsedMIDI.noteSeq[C.DURATIONINDEX][start:end], newElementSeq])
    mutateTree(start, end, target, newElementarySeq)


def pitchShifting(start, end, target):
    move = random.randint(1, 7)
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

    rand_value = random.seed()
    new_num = hash(("mutation", target.signature, rand_value))
    newElementSeq = [new_num]*(end-start)
    target.parsedMIDI.noteSeq[C.PITCHINDEX][start:end] = newPitchSeq
    target.parsedMIDI.noteSeq[C.ELEMENTINDEX][start:end] = newElementSeq
    newElementarySeq = np.vstack(
        [newPitchSeq, target.parsedMIDI.noteSeq[C.DURATIONINDEX][start:end], newElementSeq])
    mutateTree(start, end, target, newElementarySeq)


def mutateTree(start, end, target, newElementarySeq):
    # tree mutation
    # TODO: filler tree
    fillerTree = MusicTree.treeNode(
        "mutated", 0,
        newElementarySeq[0],
        newElementarySeq[1],
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
    population.sort(key=lambda x: x.fitness, reverse=True)
    for i in population:
        if i.isAncestor != True:
            return i
    return None


def selectRandomElement(individual):
    # selected element can not be signature
    element_number_set = individual.allElementGroups.copy()
    element_number_set.remove(individual.signature)
    selected_element_number = random.sample(element_number_set, 1)
    point = []
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
    # print(point)
    return point


if __name__ == "__main__":

    try:
        paths = sys.argv[1:]
    except:
        print("Missing input MIDI file!")

    population = []
    initialAncestors = []

    for path in paths:
        db = ZODB(path)
        dbroot = db.dbroot
        initialAncestors.append(dbroot[0])
        for key in dbroot.keys():
            population.append(dbroot[key])
        db.close()

    # print(ids)
    new_population = startGA(initialAncestors, population,
                             max_population=10, max_generation=2)
    # bestOffspring = findBestOffspring(new_population)
    bestOffspring = population[0]

    if bestOffspring != None:
        bestOffspring.parsedMIDI.printMIDI()
        mid_output = Demo.parsed2MIDI(bestOffspring.parsedMIDI)
        cur_time = str(time.strftime('%m_%d_%H_%M', time.localtime()))
        mid_output.save('../output/' + cur_time + ".mid")
