from hashlib import new
import sys
import time
from mido import MidiFile
from Feature import main
import Preprocess
import MusicSegmentation_2
from Individual import Individual
from Fitness import updateFitness
from ILBDM import ILBDM
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

        # TODO control how many individuals will be mutated.
        ''' Adding some variations to the offspring using mutation. '''
        # offspring_mutation = mutation(population)

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
        # print("cutting point: \n", main_parent.cuttingPoint)
        # print("signature: \n", main_parent.signature)
        # find elements to be crossovered
        invalid_elements_start_index = []
        for signature in main_parent.signature:
            invalid_elements_start_index.append(signature[1]-1)
        relative_elements = []
        for elementGroup in main_parent.allElementGroups:
            elements = []
            for element in elementGroup:
                elements.append(element[1]-1)
            relative_elements.append(elements)
        # print("all signature: \n", main_parent.allElementGroups)
        while True:
            point = []
            indexOfSelectedElement = random.randint(
                0, len(main_parent.cuttingPoint)-2)
            cuttingPoint = main_parent.cuttingPoint
            if cuttingPoint[indexOfSelectedElement] not in invalid_elements_start_index:
                for elements in relative_elements:
                    if cuttingPoint[indexOfSelectedElement] in elements:
                        for end in elements:
                            end_index = cuttingPoint.index(end)
                            start = 0 if end_index == 0 else cuttingPoint[end_index-1]+1
                            point.append((int(start), int(end)))
                        break
                if point == []:
                    end = cuttingPoint[indexOfSelectedElement]
                    start = 0 if indexOfSelectedElement == 0 else cuttingPoint[
                        indexOfSelectedElement-1]+1
                    point.append((int(start), int(end)))
                break
        point.sort(key=lambda x: x[0])
        # print("index to be crossovered: \n", point)

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
                tmp_tree_list += filler_trees
            else:
                tmp_tree_list.append(child.tree_list[t])
        child.tree_list = tmp_tree_list

        # print(child.tree_list)

        # construct noteSeq for child
        tmp_elementary_noteSeq = np.array([[], []])
        for tree in child.tree_list:
            tmp_elementary_noteSeq = np.hstack(
                [tmp_elementary_noteSeq, tree.elementary_noteSeq])
        child.parsedMIDI.noteSeq = Preprocess.expandElementarySequence(
            tmp_elementary_noteSeq)
        child.parsedMIDI.updateFieldVariable()
        child.calculateAllFeatures()

        # main_parent.details()
        # child.details()

        offspring.append(child)
    offspring.sort(key=lambda x: x.fitness, reverse=True)
    return offspring

# TODO preserve the original individual


def mutation(offspring_crossover):
    newPopulation = []
    # int(len(offspring_crossover)*0.3)
    mutation_size = len(offspring_crossover)
    count = 0
    for offspring in offspring_crossover:
        if count == mutation_size:
            break
        count = count+1
        new_parsedMIDI = Preprocess.ProcessedMIDI(None, offspring.parsedMIDI)
        newOffspring = Individual(new_parsedMIDI, offspring.cuttingPoint, offspring.allElementGroups,
                                  offspring.signature, False, offspring.ancestor)
        # selected element can not be signature
        start = 0
        end = 0
        while (start, end+1) in newOffspring.signature or (start == 0 and end == 0):
            selected_elementIndex = random.randint(
                0, len(newOffspring.cuttingPoint)-1)
            start = 0 if selected_elementIndex == 0 else newOffspring.cuttingPoint[
                selected_elementIndex-1]+1
            end = newOffspring.cuttingPoint[selected_elementIndex]
        pitchShifting(start, end, newOffspring.parsedMIDI)
        # offspring.parsedMIDI.printMIDI()
        pitchOrderReverse(start, end, newOffspring.parsedMIDI)
        newOffspring.parsedMIDI.updateFieldVariable(newOffspring.parsedMIDI)
        newOffspring.calculateAllFeatures()
        newPopulation.append(newOffspring)

    return offspring_crossover + newPopulation


def pitchOrderReverse(start, end, target):
    # Pitch
    target.noteSeq[C.PITCHINDEX][start:end +
                                 1] = np.flipud(target.noteSeq[C.PITCHINDEX][start:end+1])
    # Duration
    target.noteSeq[C.DURATIONINDEX][start:end +
                                    1] = np.flipud(target.noteSeq[C.DURATIONINDEX][start:end+1])
    # Rest
    target.noteSeq[C.RESTINDEX][start:end +
                                1] = np.flipud(target.noteSeq[C.RESTINDEX][start:end+1])
    # Interval

    def calculateInterval(i):
        if i < 0 or i >= target.numberOfNotes-1:
            return
        if target.noteSeq[C.PITCHINDEX][i+1] == 0:
            if i + 2 < target.numberOfNotes:
                nextNextPitch = target.noteSeq[C.PITCHINDEX][i+2]
                target.noteSeq[C.INTERVALINDEX][i]\
                    = abs(nextNextPitch - target.noteSeq[C.PITCHINDEX][i])
                target.noteSeq[C.INTERVALINDEX][i+1]\
                    = abs(nextNextPitch - target.noteSeq[C.PITCHINDEX][i])
            else:
                target.noteSeq[C.INTERVALINDEX][i] = 0
        else:
            target.noteSeq[C.INTERVALINDEX][i]\
                = abs(target.noteSeq[C.PITCHINDEX][i+1] - target.noteSeq[C.PITCHINDEX][i])
    for i in range(start-2, end + 2):
        calculateInterval(i)

    # TODO reconstruct accumulative beat sequence( merge into segmentation? )


def pitchShifting(start, end, target):
    move = random.randint(1, 7)
    negative = random.randint(0, 1)
    if negative == 1:
        move = move * -1
    newPitchSeq = []
    for i in range(start, end+1):
        if target.noteSeq[C.PITCHINDEX][i] != 0:
            newPitch = target.noteSeq[C.PITCHINDEX][i] + move
            if Utility.isValidPitch(newPitch):
                newPitchSeq.append(newPitch)
            else:
                return
        else:
            newPitchSeq.append(0)
    target.noteSeq[C.PITCHINDEX][start:end+1] = newPitchSeq


def findBestOffspring(population):
    population.sort(key=lambda x: x.fitness, reverse=True)
    for i in population:
        if i.isAncestor != True:
            return i
    return None


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
                             max_population=30, max_generation=2)
    bestOffspring = findBestOffspring(new_population)
    if bestOffspring != None:
        bestOffspring.parsedMIDI.printMIDI()
        mid_output = Demo.parsed2MIDI(bestOffspring.parsedMIDI)
        cur_time = str(time.strftime('%m_%d_%H_%M', time.localtime()))
        mid_output.save('../output/' + cur_time + ".mid")
