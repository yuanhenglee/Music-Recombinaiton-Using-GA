import matplotlib.pyplot as plt
import Utility
import os
import Constant as C
from zodb import ZODB, transaction
import matplotlib
import pandas as pd
import numpy as np
# from sklearn.decomposition import PCA
# from sklearn.preprocessing import StandardScaler, MinMaxScaler, Normalizer, scale
# import seaborn as sns
import copy
import csv


def calculateFeature(func):
    # params of func (parsedMIDI)
    x = []  # filename
    y = []  # feature
    directory = "../midi_file"
    for filename in os.listdir(directory):
        if filename.endswith(".mid"):
            name = filename[:-4]
            x.append(name)
            DBpath = './Music/'+name+'.fs'
            db = ZODB(DBpath)
            parsedMIDI = db.dbroot[name].parsedMIDI
            featureResult = func(parsedMIDI)
            print(featureResult)
            y.append(featureResult)
        else:
            continue
    # draw
    x_ = [1, 2, 3, 4, 5, 6, 7, 8]
    plt.plot(x_, y)
    plt.savefig(func.__name__)
    # wsl cannot use show()
    # plt.show()


def highestNote(parsedMIDI):
    return parsedMIDI.highestNote


def calPitchRatio(parsedMIDI):
    intervalCount = {0: 0, 0.5: 0, 1: 0, 1.5: 0, 2: 0, 3: 0,
                     3.5: 0, 4: 0, 4.5: 0, 5: 0, 5.5: 0, 6: 0, 7: 0}
    interval2Name = {
        0: "unison",
        0.5: "m2",
        1: "M2",
        1.5: "m3",
        2: "M3",
        3: "P4",
        3.5: "dim5",
        4: "P5",
        4.5: "m6",
        5: "M6",
        5.5: "m7",
        6: "M7",
        7: "octave"
    }
    # sort intervals into 13 categories
    # unison    m2  M2  m3  M3  P4  dim5    P5  m6  M6  m7  M7  octave
    # 0         0.5 1   1.5 2   3   3.5     4   4.5 5   5.5 6   7
    for interval in parsedMIDI.noteSeq[C.INTERVALINDEX]:
        if interval // 7 >= 1 and interval % 7 == 0:
            intervalCount[7] += 1
        else:
            intervalCount[interval % 7] += 1

    intervalFreq = {}
    for k, v in intervalCount.items():
        intervalFreq[interval2Name[k]] = v / \
            parsedMIDI.noteSeq[C.INTERVALINDEX].shape[0]

    return intervalFreq

# 21 feature from "Towards Melodic Extension Using Genetic Algorithms"

# Pitch features


def pitchVariety(parsedMIDI):
    numberOfDistinctNote = len(np.unique(parsedMIDI.noteSeq[C.PITCHINDEX]))
    variety = numberOfDistinctNote / parsedMIDI.numberOfNotes
    return variety


def pitchRange(parsedMIDI):
    # different from  "Toward..." due to different in encode
    return (parsedMIDI.highestNote - parsedMIDI.lowestNote)/14

# Tonality features


def keyCentered(parsedMIDI):
    primaryPitch = Utility.countTonicDominant(parsedMIDI.noteSeq[C.PITCHINDEX])
    return primaryPitch/parsedMIDI.numberOfNotes


def nonScaleNotes(parsedMIDI):
    nonScaleNotes = Utility.countNonScaleNote(parsedMIDI.noteSeq[C.PITCHINDEX])
    return nonScaleNotes/parsedMIDI.numberOfNotes


def dissonantIntervals(parsedMIDI):
    sumOfDissonantRating = 0

    for i in parsedMIDI.noteSeq[C.INTERVALINDEX]:
        if i == 6 or i == 11 or i >= 13 or not i.is_integer():
            sumOfDissonantRating += 1
        elif i == 10:
            sumOfDissonantRating += 0.5
    return sumOfDissonantRating/parsedMIDI.numberOfNotes

# Contour features


def contourDirection(parsedMIDI):
    risingInterval = 0
    pitchSeq = parsedMIDI.noteSeq[C.PITCHINDEX]
    for note, nextNote in zip(pitchSeq, pitchSeq[1:]):
        if note != 0 and nextNote > note:
            risingInterval += (nextNote - note)
    return risingInterval/np.sum(parsedMIDI.noteSeq[C.INTERVALINDEX])


def contourStability(parsedMIDI):
    consecutiveIntervals = 0
    pitchSeq = parsedMIDI.noteSeq[C.PITCHINDEX]
    for i in range(len(pitchSeq)-2):
        firstInterval = pitchSeq[i+1] - pitchSeq[i]
        secondInterval = pitchSeq[i+2] - pitchSeq[i+1]
        if firstInterval > 0 and secondInterval > 0:
            consecutiveIntervals += 1
        elif firstInterval == 0 and secondInterval == 0:
            consecutiveIntervals += 1
        elif firstInterval < 0 and secondInterval < 0:
            consecutiveIntervals += 1
    return consecutiveIntervals/parsedMIDI.numberOfNotes


def movementByStep(parsedMIDI):
    intervalSeq = parsedMIDI.noteSeq[C.INTERVALINDEX]
    diatonicSteps = intervalSeq[(intervalSeq < 2) & (intervalSeq > 0)]
    return diatonicSteps.size/parsedMIDI.numberOfNotes


def leapReturns(parsedMIDI):
    largeLeap = 0
    leapWithoutReturn = 0
    pitchSeq = parsedMIDI.noteSeq[C.PITCHINDEX]
    for i in range(len(pitchSeq)-2):
        firstInterval = pitchSeq[i+1] - pitchSeq[i]
        secondInterval = pitchSeq[i+2] - pitchSeq[i+1]
        if firstInterval > 4:
            largeLeap += 1
            if firstInterval * secondInterval > 0:  # no return interval
                leapWithoutReturn += 1
    if largeLeap > 0:
        return leapWithoutReturn/largeLeap
    else:
        return 1


def climaxStrength(parsedMIDI):
    pitchSeq = parsedMIDI.noteSeq[C.PITCHINDEX]
    climaxOccur = np.count_nonzero(pitchSeq == parsedMIDI.highestNote)
    if climaxOccur == 0:
        print("highestNote value ERROR")
        return 1
    return 1/climaxOccur

# Rhythmic features
# temporary multiplier due to big value in minLengthInTicks


def noteDensity(parsedMIDI):
    return 100*np.count_nonzero(parsedMIDI.noteSeq[C.PITCHINDEX] != 0) / \
        (parsedMIDI.totalDuration * parsedMIDI.minLengthInTicks)


def restDensity(parsedMIDI):
    return 100*np.count_nonzero(parsedMIDI.noteSeq[C.PITCHINDEX] == 0) / \
        (parsedMIDI.totalDuration * parsedMIDI.minLengthInTicks)


def rhythmicVariety(parsedMIDI):
    return len(np.unique(parsedMIDI.noteSeq[C.DURATIONINDEX])) / 16

# ? normalize fail on 16


def rhythmicRange(parsedMIDI):
    durationSeq = parsedMIDI.noteSeq[C.DURATIONINDEX]
    maxDuration = np.max(durationSeq)
    minDuration = np.min(durationSeq[durationSeq != 0])
    return maxDuration/(minDuration*16)

# Pattern features


def repeatedPitchPattern(parsedMIDI):
    repeatTimes = {2: 0, 3: 0, 4: 0}
    pitchSeq = parsedMIDI.noteSeq[C.PITCHINDEX]
    for i in range(len(pitchSeq)-3):
        if pitchSeq[i] == pitchSeq[i+1]:
            repeatTimes[2] += 1
            if pitchSeq[i+1] == pitchSeq[i+2]:
                repeatTimes[3] += 1
                if pitchSeq[i+2] == pitchSeq[i+3]:
                    repeatTimes[4] += 1

    return \
        repeatTimes[2]/(parsedMIDI.numberOfNotes-1),\
        repeatTimes[3]/(parsedMIDI.numberOfNotes-2),\
        repeatTimes[4]/(parsedMIDI.numberOfNotes-3)


def repeatedRhythmPattern(parsedMIDI):
    repeatTimes = {2: 0, 3: 0, 4: 0}
    durationSeq = parsedMIDI.noteSeq[C.DURATIONINDEX]
    for i in range(len(durationSeq)-3):
        if durationSeq[i] == durationSeq[i+1]:
            repeatTimes[2] += 1
            if durationSeq[i+1] == durationSeq[i+2]:
                repeatTimes[3] += 1
                if durationSeq[i+2] == durationSeq[i+3]:
                    repeatTimes[4] += 1

    return \
        repeatTimes[2]/(parsedMIDI.numberOfNotes-1),\
        repeatTimes[3]/(parsedMIDI.numberOfNotes-2),\
        repeatTimes[4]/(parsedMIDI.numberOfNotes-3)

# Other Features


def leapDensity(parsedMIDI):
    largeLeap = 0
    pitchSeq = parsedMIDI.noteSeq[C.PITCHINDEX]
    for i in range(len(pitchSeq)-1):
        interval = pitchSeq[i+1] - pitchSeq[i]
        if interval > 4:
            largeLeap += 1
    return largeLeap/(parsedMIDI.numberOfNotes-1)


def bigLeapDensity(parsedMIDI):
    largeLeap = 0
    pitchSeq = parsedMIDI.noteSeq[C.PITCHINDEX]
    for i in range(len(pitchSeq)-1):
        interval = pitchSeq[i+1] - pitchSeq[i]
        if interval > 7:
            largeLeap += 1
    return largeLeap/(parsedMIDI.numberOfNotes-1)


def sumOfSquareOfInterval(parsedMIDI):
    return sum(i*i for i in parsedMIDI.noteSeq[C.INTERVALINDEX])


def standardization(df_features):
    tmp_features = copy.deepcopy(df_features)
    path_Data = "../test & learn/EDA Result/songMeanSTD.csv"
    data = pd.read_csv(path_Data)
    mean = data["mean"]
    std = data["std"]
    for i, feature in enumerate(tmp_features):
        # print(feature)
        tmp_features[feature] = (tmp_features[feature] -
                                 mean[i])/std[i]
    return tmp_features

def intervalBtwElement(parsedMIDI):
    dict_interval = dict()
    cur_number = parsedMIDI.noteSeq[C.ELEMENTINDEX][0]
    for i, number in enumerate(parsedMIDI.noteSeq[C.ELEMENTINDEX]):
        if number != cur_number:
            interval = int(parsedMIDI.noteSeq[C.INTERVALINDEX][i-1])
            dict_interval[interval] = dict_interval.get(interval, 0)+1
            cur_number = number
    dict_interval = dict(
        sorted(dict_interval.items(), key=lambda item: item[1], reverse=True))
    return dict_interval


def main():

    # get data from DB
    directory = "../midi_file"
    names = []
    parsedMIDIs = []
    for filename in os.listdir(directory):
        if filename.endswith(".mid"):
            name = filename[:-4]
            DBpath = './Music/'+name+'.fs'
            db = ZODB(DBpath)
            parsedMIDI = db.dbroot[0].parsedMIDI
            names.append(name)
            parsedMIDIs.append(parsedMIDI)

    # construct features df
    f_repeatedPitch_2 = [repeatedPitchPattern(i)[0] for i in parsedMIDIs]
    f_repeatedRhythmic_2 = [repeatedPitchPattern(i)[0] for i in parsedMIDIs]
    f_repeatedPitch_3 = [repeatedPitchPattern(i)[1] for i in parsedMIDIs]
    f_repeatedRhythmic_3 = [repeatedPitchPattern(i)[1] for i in parsedMIDIs]
    f_repeatedPitch_4 = [repeatedPitchPattern(i)[2] for i in parsedMIDIs]
    f_repeatedRhythmic_4 = [repeatedPitchPattern(i)[2] for i in parsedMIDIs]

    df_songFeatures = pd.DataFrame({
        "name":   names,
        "Pitch Variety":   [pitchVariety(i) for i in parsedMIDIs],
        "Pitch Range":   [pitchRange(i) for i in parsedMIDIs],
        "Key Centered":   [keyCentered(i) for i in parsedMIDIs],
        "Non-scale Notes":   [nonScaleNotes(i) for i in parsedMIDIs],
        "Dissonant Intervals":   [dissonantIntervals(i) for i in parsedMIDIs],
        "Contour Direction":   [contourDirection(i) for i in parsedMIDIs],
        "Contour Stability":   [contourStability(i) for i in parsedMIDIs],
        "Movement by Step":   [movementByStep(i) for i in parsedMIDIs],
        "Leap Returns":   [leapReturns(i) for i in parsedMIDIs],
        "Climax Strength":   [climaxStrength(i) for i in parsedMIDIs],
        "Note Density":   [noteDensity(i) for i in parsedMIDIs],
        "Rest Density":   [restDensity(i) for i in parsedMIDIs],
        "Rhythmic Variety":   [rhythmicVariety(i) for i in parsedMIDIs],
        "Rhythmic Range":   [rhythmicRange(i) for i in parsedMIDIs],
        "Repeated Pitch_2":   f_repeatedPitch_2,
        "Repeated Rhythm_2":   f_repeatedRhythmic_2,
        "Repeated Pitch_3":   f_repeatedPitch_3,
        "Repeated Rhythm_3":   f_repeatedRhythmic_3,
        "Repeated Pitch_4":   f_repeatedPitch_4,
        "Repeated Rhythm_4":   f_repeatedRhythmic_4,
        "LeapDensity":      [leapDensity(i) for i in parsedMIDIs],
        "BigLeapDensity":      [bigLeapDensity(i) for i in parsedMIDIs],
        "SumOfSquareOfInterval": [sumOfSquareOfInterval(i) for i in parsedMIDIs]
    })

    # normalized features
    df_songFeatures.to_csv(
        "../test & learn/EDA Result/songFeatures.csv")

    # numeric features only
    df_numeric = df_songFeatures.drop(columns='name')

    df_MeanSTD = pd.DataFrame({
        "mean": df_numeric.mean(numeric_only=True),
        "std": df_numeric.std(numeric_only=True),
        "CV": df_numeric.std(numeric_only=True)/df_numeric.mean(numeric_only=True),
        "P25": df_numeric.quantile(0.25, numeric_only=True),
        "P50": df_numeric.quantile(0.5, numeric_only=True),
        "P75": df_numeric.quantile(0.75, numeric_only=True),
        "IQR": df_numeric.quantile(0.75, numeric_only=True)-df_numeric.quantile(0.25, numeric_only=True),
        "min": df_numeric.min(numeric_only=True),
        "max": df_numeric.max(numeric_only=True)
    })

    # df.sort_values(by=[''])
    df_MeanSTD.to_csv("../test & learn/EDA Result/songMeanSTD.csv")
    df_MeanSTD = df_MeanSTD.sort_values(by=['CV'])
    df_MeanSTD.to_csv("../test & learn/EDA Result/songMeanSTD_ordered.csv")

    # interval between element

    dict_allInterval = dict()
    for i in parsedMIDIs:
        x = dict_allInterval
        y = intervalBtwElement(i)
        dict_allInterval = {k: x.get(k, 0) + y.get(k, 0)
                            for k in set(x) | set(y)}
    # print(dict_allInterval)

    '''
    # corr
    sns_plot = sns.heatmap(df_numeric.corr(), annot=True)
    sns_plot.figure.savefig("../test & learn/EDA Result/corrHeatmap.pdf")

    # PCA
    df_st = pd.DataFrame(StandardScaler().fit_transform(df_numeric))

    # Make biplot with the number of features
    # get PC scores
    pca_scores = PCA().fit_transform(df_numeric)

    # get 2D biplot
    import plotly
    import plotly.express as px
    fig = px.scatter(pca_scores, x=0, y=1, color=df_songFeatures['name'])
    plotly.offline.plot(fig, filename='../test & learn/EDA Result/PCA.html')
    # fig.savefig("../test & learn/EDA Result/PCA.pdf")

    '''

    # exploring pitch of long notes
    # long_notes_pitch = {}
    # for count, parsedMIDI in enumerate(parsedMIDIs):
    #     for i in range(parsedMIDI.numberOfNotes):
    #         if parsedMIDI.noteSeq[C.DURATIONINDEX][i] > max(4, np.percentile(parsedMIDI.noteSeq[C.DURATIONINDEX], 75)):
    #             pitch = (float(parsedMIDI.noteSeq[C.PITCHINDEX][i]%7))
    #             if not pitch.is_integer(): print(names[count])
    #             if pitch in long_notes_pitch: 
    #                 long_notes_pitch[pitch] += 1
    #             else:
    #                 long_notes_pitch[pitch] = 1
    # long_notes_pitch = sorted(long_notes_pitch.items(), key=lambda x: x[1], reverse=True)
    # print(long_notes_pitch)
    # exploring end of song
    # last_note= {'up':0, 'down':0, 'm':0, 'v':0, 'flat': 0}
    # for count, parsedMIDI in enumerate(parsedMIDIs):
    #     last_interval = float(parsedMIDI.noteSeq[C.PITCHINDEX][-1] - parsedMIDI.noteSeq[C.PITCHINDEX][-2])
    #     last_2_interval = float(parsedMIDI.noteSeq[C.PITCHINDEX][-2] - parsedMIDI.noteSeq[C.PITCHINDEX][-3])
    #     if parsedMIDI.noteSeq[C.PITCHINDEX][-1] == 0:
    #         last_interval = float(parsedMIDI.noteSeq[C.PITCHINDEX][-2] - parsedMIDI.noteSeq[C.PITCHINDEX][-3])
    #         last_2_interval = float(parsedMIDI.noteSeq[C.PITCHINDEX][-3] - parsedMIDI.noteSeq[C.PITCHINDEX][-4])

    #     if last_interval < 0:
    #         if last_2_interval <= 0:
    #             last_note['down'] += 1
    #         else:
    #             last_note['v'] += 1
    #     elif last_interval > 0:
    #         if last_2_interval < 0:
    #             last_note['m'] += 1
    #         else:
    #             last_note['up'] += 1
    #     else:
    #         if last_2_interval < 0:
    #             last_note['down'] += 1
    #         elif last_2_interval > 0:
    #             last_note['up'] += 1
    #         else:
    #             last_note['flat'] += 1
    # print(last_note)



if __name__ == '__main__':
    # import cProfile
    # import pstats
    # with cProfile.Profile() as pr:
    main()

    # stats = pstats.Stats(pr)
    # stats.sort_stats(pstats.SortKey.TIME)
    # # stats.print_stats()
