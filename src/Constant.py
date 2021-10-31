from numpy.core.fromnumeric import std
import pandas as pd


DESIRE_AVG_DURATION = 4
BREAK = 0
PITCHINDEX = 0
DURATIONINDEX = 1
INTERVALINDEX = 2
RESTINDEX = 3
# accumulative beat count
ACCUMULATIVEINDEX = 4
SEGMENTATIONINDEX = 5
ELEMENTINDEX = 6

BeatInMeasure = 16
AccumulativeWeight = 3

MINRPLENTH = 3


NUMBER_FEATURES = 23
NUMBER_SONGS = 97

INPUT_NAMES = []
INPUT_RATE = 0.5

FITNESS_WEIGHT = [1, 2, 5, 200, 500, 1]


consensus_weight = pd.DataFrame(
    {
        "Pitch Variety":   [0],
        "Pitch Range":  [1],
        "Key Centered":   [1],
        "Non-scale Notes":   [1],
        "Dissonant Intervals":   [1],
        "Contour Direction":   [0],
        "Contour Stability":   [0],
        "Movement By Step":   [0],
        "Leap Returns":   [1],
        "Climax Strength":   [1],
        "Note Density":   [0],
        "Rest Density":   [0],
        "Rhythmic Variety":   [0],
        "Rhythmic Range":   [1],
        "Repeated Pitch_2":  [0],
        "Repeated Rhythm_2":  [0],
        "Repeated Pitch_3":  [0],
        "Repeated Rhythm_3":  [0],
        "Repeated Pitch_4":  [0],
        "Repeated Rhythm_4":  [0],
        "LeapDensity":      [1],
        "BigLeapDensity":      [1],
        "SumOfSquareOfInterval": [1]
    }
)
similarity_weight = pd.DataFrame(
    {
        "Pitch Variety":   [0],
        "Pitch Range":  [0],
        "Key Centered":   [1],
        "Non-scale Notes":   [1],
        "Dissonant Intervals":   [1],
        "Contour Direction":   [1],
        "Contour Stability":   [1],
        "Movement By Step":   [1],
        "Leap Returns":   [0],
        "Climax Strength":   [0],
        "Note Density":   [1],
        "Rest Density":   [1],
        "Rhythmic Variety":   [0],
        "Rhythmic Range":   [0],
        "Repeated Pitch_2":  [1],
        "Repeated Rhythm_2":  [1],
        "Repeated Pitch_3":  [1],
        "Repeated Rhythm_3":  [1],
        "Repeated Pitch_4":  [1],
        "Repeated Rhythm_4":  [1],
        "LeapDensity":      [1],
        "BigLeapDensity":      [1],
        "SumOfSquareOfInterval": [1]
    }
)
