
def whetherItsInRange(lower, upper, value):
    score = 0
    if value >= lower and value <= upper:
        score += 1
    else:
        score += 0
    return score


def updateFitness(individual):
    # skip update if already been calculated
    if individual.fitness != -1:
        return
    # else: give fitness val
    individual.fitness = 0

    # punishing individual out of range
    restRate_UpperBound = 0.07
    restRate_LowerBound = 0
    noteDensity_UpperBound = 0.52
    noteDensity_LowerBound = 0.4
    pitchRange_UpperBound = 16
    pitchRange_LowerBound = 10

    individual.fitness += whetherItsInRange(restRate_LowerBound,
                                            restRate_UpperBound, individual.restRate)
    individual.fitness += whetherItsInRange(noteDensity_LowerBound,
                                            noteDensity_UpperBound, individual.noteDensity)
    individual.fitness += whetherItsInRange(pitchRange_LowerBound,
                                            pitchRange_UpperBound, individual.pitchRange)

    

