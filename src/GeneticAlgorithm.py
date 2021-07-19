from hashlib import new
import sys
from mido import MidiFile
from Preprocess import ProcessedMIDI
import MusicSegmentation_2
from Individual import Individual
from Fitness import updateFitness
from ILBDM import ILBDM
import Constant as C

import numpy as np
import random


def startGA(num_generations, num_parents_mating, population, max_population):
    for generation in range(num_generations):
        # Measuring the fitness of each chromosome in the population.
        for individual in population:
            updateFitness(individual)
        population.sort(key=lambda x: x.fitness)
        population = population[0:max_population]
        print("\n", population[0].parsedMIDI.noteSeq[C.INTERVALINDEX])
        print( population[0].intervalRatios )

        # terminate

        # Selecting the best parents in the population for mating.
        parents = select_mating_pool(population, num_parents_mating)

        # Generating next generation using crossover.
        offspring_crossover = crossover(
            parents, offspring_size=(max_population-num_parents_mating))

        # TODO control how many individuals will be mutated.
        # Adding some variations to the offspring using mutation.
        offspring_mutation = mutation(offspring_crossover)

        # Creating the new population based on the parents and offspring.
        population[len(population):] = offspring_mutation
    return population


def select_mating_pool(population, num_parents_mating):
    # Selecting the best individuals in the current generation as parents for producing the offspring of the next generation.
    population.sort(key=lambda x: x.fitness)

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
            mask = np.zeros(len(main_parent.cuttingPoint))
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

            offspring_parsedMIDI = ProcessedMIDI( None, main_parent.parsedMIDI )
            offspring_ancestorMIDI = main_parent.parsedMIDI

            ####change to individual####
            # find cutting Point
            offspring_LBDM = ILBDM(offspring_parsedMIDI)
            offspring_cuttingPoint = MusicSegmentation_2.musicSegmentation2(
                offspring_parsedMIDI, offspring_LBDM)
            offspring.append(Individual(offspring_parsedMIDI, offspring_ancestorMIDI,
                                        offspring_cuttingPoint, main_parent.signature))

    return offspring[0:offspring_size]

# TODO preserve the original individual
def mutation(offspring_crossover):
    for offspring in offspring_crossover:
        # selected element can not be signature
        start = 0
        end = 0
        while (start, end+1) in offspring.signature or (start == 0 and end == 0):
            selected_elementIndex = random.randint(
                0, len(offspring.cuttingPoint)-1)
            start = 0 if selected_elementIndex == 0 else offspring.cuttingPoint[
                selected_elementIndex-1]+1
            end = offspring.cuttingPoint[selected_elementIndex]
        pitchShifting(start, end, offspring.parsedMIDI)
        pitchOrderReverse(start, end, offspring.parsedMIDI)
    return offspring_crossover

def pitchOrderReverse( start, end, target ): 
    targetSegment = target.noteSeq[C.PITCHINDEX][start:end+1]
    target.noteSeq[C.PITCHINDEX][start:end+1] = targetSegment[::-1]
    print( "reversed:",start, end)

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
        LBDM_result = ILBDM(parsedMIDI)
        cuttingPoint = MusicSegmentation_2.musicSegmentation2(
            parsedMIDI, LBDM_result)
        signaturePossibilities = MusicSegmentation_2.extractSignatures(
            parsedMIDI)
        for signature in signaturePossibilities:
            population.append(Individual(
                parsedMIDI, parsedMIDI, cuttingPoint, signature))

    # print("BEFORE:")
    # for individual in population:
    #     individual.printIndividual()

    new_population = startGA(10, 5, population, 10)

    # print("AFTER:")
    # for individual in new_population:
    #     individual.printIndividual()
