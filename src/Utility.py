def formattedPrint(target):
    for i in range(len(target)):
        print("%3s" % (target[i]), end='')
    print()

def recodePitch( n ):
    stepDiff2Interval = {0:1, 1:1.5 , 2:2, 3:2.5, 4:3, 5:4, 6:4.5, 7:5, 8:5.5, 9:6, 10:6.5, 11:7}
    if n%12 in stepDiff2Interval:
        return 7*(n//12-3) + stepDiff2Interval[n%12]
    else:
        raise ValueError

def value2Pitch( value ):
    if value == 0:
        return "-"
    if not value % 1 == 0:
        return "?"
    value = int(value)
    octave = value//7 + 2
    notationNameTable = {1:'C', 2:'D', 3:'E', 4:'F', 5:'G', 6:'A', 0:'B'}
    return notationNameTable[value%7] + str(octave)