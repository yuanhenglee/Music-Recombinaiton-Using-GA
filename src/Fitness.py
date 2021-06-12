
def calculateFitness(lower, upper, value):
    score = 0
    if value >= lower and value <= upper:
        score += 1
    else:
        score += 0
    return score


def updatefitness(individual):
    individual.fitness = 0
    restRate_UpperBound = 0.07
    restRate_LowerBound = 0
    noteDensity_UpperBound = 0.52
    noteDensity_LowerBound = 0.4
    pitchRange_UpperBound = 16
    pitchRange_LowerBound = 10

    individual.fitness += calculateFitness(restRate_LowerBound,
                                           restRate_UpperBound, individual.restRate)
    individual.fitness += calculateFitness(noteDensity_LowerBound,
                                           noteDensity_UpperBound, individual.noteDensity)
    individual.fitness += calculateFitness(pitchRange_LowerBound,
                                           pitchRange_UpperBound, individual.pitchRange)
