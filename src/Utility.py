
import numpy as np

def formattedPrint(target):
    for i in range(len(target)):
        print("%4s" % (target[i]), end='')
    print()

# as a inverse func of recodePitch
def pitch2MIDIPitch( pitch ):
    interval2stepdiff = {0:11, 1:0, 1.5:1 , 2:2, 2.5:3, 3:4, 4:5, 4.5:6, 5:7, 5.5:8, 6:9, 6.5:10, 7:11}

    MIDIPitch = int( ((pitch-1)//7+3)*12 + interval2stepdiff[pitch%7] )
    if 0<MIDIPitch<108: return MIDIPitch
    else: raise ValueError("MIDIPitch out of range")

def isValidPitch( pitch ):
    if pitch <= 0: return False
    elif pitch >= 36: return False
    elif pitch%7 not in {1, 1.5, 2, 2.5, 3, 4, 4.5, 5, 5.5, 6, 6.5, 0}: return False
    return True

def recodePitch( n ):
    """                           
        range: c2 to c7
        c2 in midi: 36 -> 1
        c6 in midi: 84 -> 29
        c7 in midi: 96 -> 36
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

# if __name__ == '__main__':
#     arr = np.random.randint( low=36, high=85, size=10000 )
#     arr1 = [pitch2MIDIPitch(recodePitch(i)) for i in arr]
#     for i, j in zip( arr, arr1 ):
#         print( i,j )