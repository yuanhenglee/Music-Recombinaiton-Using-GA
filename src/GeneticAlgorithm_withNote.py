from hashlib import new
import sys
import os
import time
from mido import MidiFile
from Feature import main
import Preprocess
import MusicSegmentation_2
from Individual import Individual
from Fitness_withNote import updateFitness
from ILBDM import ILBDM, ILBDM_elementary_noteSeq
import Utility
import Constant as C
from contextlib import redirect_stdout

import numpy as np
import random
from zodb import ZODB, transaction
import copy
import Demo
import MusicTree


def startGA(initialAncestors, population, mutation_rate=0.3, crossover_rate=0.3, max_generation=1000, max_population=1000, n_generation_terminate=100, generation_to_kill=10):
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
        # construct offspring based on main_parent
        child = copy.deepcopy(main_parent)
        child.isAncestor = False
        child.ancestor = initialAncestors

        main_parent_length = main_parent.parsedMIDI.numberOfNotes
        # print("main_parent_length: ", main_parent_length)
        sub_parent_length = sub_parent.parsedMIDI.numberOfNotes
        # print("sub_parent_length: ", sub_parent_length)
        child_noteSeq = child.parsedMIDI.noteSeq
        elementarySequence = np.vstack(
            [child_noteSeq[C.PITCHINDEX], child_noteSeq[C.DURATIONINDEX]])
        mask = np.random.randint(2, size=main_parent_length)
        # print("mask: ", mask)
        # print("before pitch: ", child_noteSeq[C.PITCHINDEX])
        tmp_element_number_list = child_noteSeq[C.ELEMENTINDEX]
        for i in range(main_parent_length):
            if mask[i] == 1:
                elementarySequence[0][i] = sub_parent.parsedMIDI.noteSeq[C.PITCHINDEX][i %
                                                                                       sub_parent_length]
                elementarySequence[1][i] = sub_parent.parsedMIDI.noteSeq[C.DURATIONINDEX][i %
                                                                                          sub_parent_length]
                tmp_element_number_list[i] = sub_parent.parsedMIDI.noteSeq[C.ELEMENTINDEX][i %
                                                                                           sub_parent_length]
        child.parsedMIDI.noteSeq = Preprocess.expandElementarySequence(
            elementarySequence)
        child.parsedMIDI.noteSeq[C.ELEMENTINDEX] = tmp_element_number_list
        # print("after pitch: ", child.parsedMIDI.noteSeq[C.PITCHINDEX])

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

        child_length = child.parsedMIDI.numberOfNotes
        child_noteSeq = child.parsedMIDI.noteSeq
        elementarySequence = np.vstack(
            [child_noteSeq[C.PITCHINDEX], child_noteSeq[C.DURATIONINDEX]])
        mask = np.random.choice(2, child_length, p=[0.8, 0.2])
        # print("mask: ", mask)
        # print("before pitch: ", child_noteSeq[C.PITCHINDEX])
        for i in range(child_length):
            if mask[i] == 1:
                is_negative = np.random.randint(2)
                move = 3
                if is_negative == 1:
                    move *= -1
                elementarySequence[0][i] += move
        tmp_element_number_list = child.parsedMIDI.noteSeq[C.ELEMENTINDEX]
        child.parsedMIDI.noteSeq = Preprocess.expandElementarySequence(
            elementarySequence)
        child.parsedMIDI.noteSeq[C.ELEMENTINDEX] = tmp_element_number_list
        # print("after pitch: ", child.parsedMIDI.noteSeq[C.PITCHINDEX])

        child.parsedMIDI.updateFieldVariable(child.parsedMIDI)
        child.calculateAllFeatures()
        newPopulation.append(child)

    return newPopulation


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

    # load date from db
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

    #construct output dir
    src_name = C.INPUT_NAMES[0]  + '&' + C.INPUT_NAMES[1]
    cur_time = str(time.strftime('%H_%M_%S', time.localtime()))
    output_name = src_name + cur_time + "_withNote" 
    output_path = "../output/" + output_name
    os.makedirs( output_path )

    with open(output_path+'/log.txt', 'w') as f:
        with redirect_stdout(f):
            # starting GA!    
            new_population = startGA(initialAncestors, population,
                                    max_population=30, max_generation=1000)
            bestOffspring = findBestOffspring(new_population)

            bestOffspring.parsedMIDI.printMIDI()
            mid_output = Demo.parsed2MIDI(bestOffspring.parsedMIDI)
            mid_output.save( output_path + '/' + output_name + ".mid")
            dbpath = output_path + "/" + output_name + ".fs"
            db = ZODB(dbpath)
            db.dbroot["Individual"] = bestOffspring
            transaction.commit()
            db.close()
