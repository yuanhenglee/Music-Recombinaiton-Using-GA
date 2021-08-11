from hashlib import new
import sys
from mido import MidiFile
from Feature import main
from Preprocess import ProcessedMIDI
import MusicSegmentation_2
from Individual import Individual
from Fitness import updateFitness
from ILBDM import ILBDM
import Constant as C

import numpy as np
import random
from zodb import ZODB, transaction
import copy


def startGA(num_generations, num_parents_mating, population, max_population):
    for generation in range(num_generations):
        # Measuring the fitness of each chromosome in the population.
        for individual in population:
            updateFitness(individual)
        population.sort(key=lambda x: x.fitness, reverse=True)
        population = population[0:max_population]
        print("==================\ngeneration: \n", generation)
        for individual in population:
            if individual.isAncestor:
                continue
            else:
                print(round(individual.fitness, 6))
        # print("\n", population[0].parsedMIDI.noteSeq[C.INTERVALINDEX])

        # terminate

        # Selecting the best parents in the population for mating.
        parents = select_mating_pool(population, num_parents_mating)

        # Generating next generation using crossover.
        offspring_crossover = population + crossover(
            parents, max_population-num_parents_mating)
        # offspring_crossover = crossover(parents)

        # TODO control how many individuals will be mutated.
        # Adding some variations to the offspring using mutation.
        offspring_crossover.sort(key=lambda x: x.fitness, reverse=True)
        offspring_mutation = mutation(offspring_crossover)

        # Creating the new population based on the parents and offspring.
        population = offspring_mutation
    return population


def select_mating_pool(population, num_parents_mating):
    # Selecting the best individuals in the current generation as parents for producing the offspring of the next generation.
    population.sort(key=lambda x: x.fitness, reverse=True)

    parents = population[0:num_parents_mating]

    return parents


def crossover(parents, offspring_size):
    offspring = []
    for main_parent in parents:
        for sub_parent in parents:
            if main_parent == sub_parent:
                continue

            """         
            move this part to preprocess
            # change OG_mido to null
            offspring_parsedMIDI.OG_Mido = None
            # update min length in ticks
            offspring_parsedMIDI.minLengthInTicks = np.gcd(
                main_parent.parsedMIDI.minLengthInTicks, sub_parent.parsedMIDI.minLengthInTicks) 
            """

            ####Crossover####
            # mask of main parent
            mask = np.zeros(len(main_parent.cuttingPoint)-1)
            # signature is 1
            tmp_signature = set() | main_parent.signature
            while len(tmp_signature) != 0:
                signature = tmp_signature.pop()
                index = main_parent.cuttingPoint.index(signature[1]-1)
                mask[index] = 1
            # others 0 or 1
            for i in range(len(mask)):
                if(mask[i] == 0):
                    mask[i] = random.randint(0, 1)
            # crossover
            # TODO
            # TEST (random)
            temp = ProcessedMIDI(None, main_parent.parsedMIDI)
            for i in range(len(mask)):
                if(mask[i] == 1):
                    start = main_parent.cuttingPoint[i]
                    end = main_parent.cuttingPoint[i+1]-1
                    for i in range(start, end+1):
                        move = random.randint(-4, 4)
                        if temp.noteSeq[C.PITCHINDEX][i] != 0:
                            if temp.noteSeq[C.PITCHINDEX][i] + move <= 0:
                                break
                            temp.noteSeq[C.PITCHINDEX][i] = temp.noteSeq[C.PITCHINDEX][i] + move

            ####
            # offspring_parsedMIDI = ProcessedMIDI(None, main_parent.parsedMIDI)
            offspring_parsedMIDI = ProcessedMIDI(None, temp)
            offspring_ancestor = main_parent.ancestor

            ####change to individual####
            # TODO: update cutting Point
            offspring.append(Individual(offspring_parsedMIDI,
                                        main_parent.cuttingPoint, main_parent.signature, False, offspring_ancestor))
    offspring.sort(key=lambda x: x.fitness, reverse=True)
    return offspring[0:offspring_size]

# TODO preserve the original individual


def mutation(offspring_crossover):
    newPopulation = []
    mutation_size = int(len(offspring_crossover)*0.3)
    count = 0
    for offspring in offspring_crossover:
        if count == mutation_size:
            break
        count = count+1
        new_parsedMIDI = ProcessedMIDI(None, offspring.parsedMIDI)
        newOffspring = Individual(new_parsedMIDI, offspring.cuttingPoint,
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
    move = random.randint(-7, 7)
    newPitch = []
    for i in range(start, end+1):
        if target.noteSeq[C.PITCHINDEX][i] != 0:
            if target.noteSeq[C.PITCHINDEX][i] + move <= 0:
                return
            newPitch.append(target.noteSeq[C.PITCHINDEX][i] + move)
        else:
            newPitch.append(0)
    target.noteSeq[C.PITCHINDEX][start:end+1] = newPitch


if __name__ == "__main__":

    try:
        paths = sys.argv[1:]
    except:
        print("Missing input MIDI file!")

    population = []

    for path in paths:
        mid = MidiFile(path)
        parsedMIDI = ProcessedMIDI(mid)
        parsedMIDI.printMIDI()
        LBDM_result = ILBDM(parsedMIDI)
        cuttingPoint = MusicSegmentation_2.musicSegmentation2(
            parsedMIDI, LBDM_result)
        signaturePossibilities = MusicSegmentation_2.extractSignatures(
            parsedMIDI)
        print(signaturePossibilities)
        for signature in signaturePossibilities:
            population.append(Individual(
                parsedMIDI, cuttingPoint, signature, True))

    new_population = startGA(20, 5, population, 20)
    new_population.sort(key=lambda x: x.fitness, reverse=True)
