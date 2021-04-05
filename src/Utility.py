def formattedPrint(target):
    for i in range(len(target)):
        print("%3s" % (target[i]), end='')
    print()

def value2Pitch( value ):
    octave = value//7 + 2
    notationNameTable = {1:'C', 2:'D', 3:'E', 4:'F', 5:'G', 6:'A', 7:'B'}
    return notationNameTable[value%7 + 1] + str(octave)