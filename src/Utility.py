
import numpy as np

def formattedPrint(target):
    for i in range(len(target)):
        print("%4s" % (target[i]), end='')
    print()

def recodePitch( n ):
    """                           
        range: c2 to c6
        c2 in midi: 36 -> 1
        c6 in midi: 84 -> 29
        formula: 
        T(n) = 7*(n//12-3) + stepDiff2Interval(n%12)
    """
    stepDiff2Interval = {0:1, 1:1.5 , 2:2, 3:2.5, 4:3, 5:4, 6:4.5, 7:5, 8:5.5, 9:6, 10:6.5, 11:7}
    if n%12 in stepDiff2Interval:
        return 7*(n//12-3) + stepDiff2Interval[n%12]
    else:
        raise ValueError

def value2Pitch( value ):
    sharp = ""
    if value == 0:
        return "-"
    if not value == int(value):
        sharp = "#"
    value = int(value)
    octave = value//7 + 2
    notationNameTable = {1:'C', 2:'D', 3:'E', 4:'F', 5:'G', 6:'A', 0:'B'}
    return sharp + notationNameTable[value%7] + str(octave)

def countTonicDominant( pitchSeq ):
    tonicCount = np.count_nonzero( pitchSeq % 7 == 1 )
    DominantCount = np.count_nonzero( pitchSeq % 7 == 5 )
    return tonicCount+DominantCount

def countNonScaleNote( pitchSeq ):
    NonScaleCount = 0
    for i in pitchSeq:
        if not i.is_integer():
            NonScaleCount+=1
    return NonScaleCount 
