import sys
from mido import MidiFile
from Preprocess import ProcessedMIDI
import MusicSegmentation_2
from Individual import Individual
from Fitness import updateFitness


def startGA(num_generations, num_parents_mating, population):
    for generation in range(num_generations):
        # Measuring the fitness of each chromosome in the population.
        for individual in population:
            updateFitness(individual)
        # Selecting the best parents in the population for mating.
        parents = select_mating_pool(population, num_parents_mating)

        # Generating next generation using crossover.
        offspring_crossover = crossover(parents, offspring_size=(len(population)-num_parents_mating) )

        # Adding some variations to the offsrping using mutation.
        offspring_mutation = mutation(offspring_crossover)

        # Creating the new population based on the parents and offspring.
        population[0:len(parents)] = parents
        population[len(parents):] = offspring_mutation
    return population


def select_mating_pool( population, num_parents_mating ):
    # Selecting the best individuals in the current generation as parents for producing the offspring of the next generation.
    population.sort( key = lambda x: x.fitness )

    parents = population[0:num_parents_mating]

    return parents

def crossover(parents, offspring_size):
    return parents[0:offspring_size]

def mutation(offspring_crossover):
    return offspring_crossover

if __name__ == "__main__":

    try:
        paths = sys.argv[1:]
    except:
        print("Missing input MIDI file!")

    population = []

    for path in paths:
        mid = MidiFile(path)
        parsedMIDI = ProcessedMIDI(mid)
        signaturePossibilities = MusicSegmentation_2.extractSignatures(
            parsedMIDI)
        for signature in signaturePossibilities:
            population.append(Individual(parsedMIDI, parsedMIDI, signature))

    print("BEFORE:")
    for individual in population:
        individual.printIndividual()

    new_population = startGA(3, 5, population)

    print("AFTER:")
    for individual in new_population:
        individual.printIndividual()
