from mido import MidiFile
from math import gcd

mid = MidiFile("C:/Users/user/Documents/code/Music Recombination/midi_file/bee.mid")
gcd_value = 0
min_value = 109
max_value = 20
note_arr = []
length_arr = []


def findMaxMin(note):
    global max_value, min_value
    if note > max_value:
        max_value = note
    if note < min_value:
        min_value = note


def combine(gcd_value, n):
    global note_arr, length_arr
    note_arr2 = []
    index = 0
    for i in range(len(note_arr)):
        for j in range((int)(length_arr[i]/gcd_value)):
            if j == 0:
                note_arr2.append(note_arr[i])
            else:
                note_arr2.append(n+1)
    print(note_arr2)


# 計算gcd
for i, track in enumerate(mid.tracks):
    for msg in track:
        if msg.type == 'note_on':
            findMaxMin(msg.note)
            if msg.time != 0 and gcd_value != 0:
                gcd_value = gcd(gcd_value, msg.time)
        elif msg.type == 'note_off':
            if gcd_value == 0:
                gcd_value = msg.time
            else:
                gcd_value = gcd(gcd_value, msg.time)
# 音高編碼
for i, track in enumerate(mid.tracks):
    for msg in track:
        if msg.type == 'note_on':
            # 紀錄休止符為0
            if note_arr != [] and msg.time != 0:
                note_arr.append(0)
                length_arr.append(msg.time)
        elif msg.type == 'note_off':
            # 紀錄音
            note_arr.append(msg.note - min_value + 1)
            length_arr.append(msg.time)

print(note_arr)
print(length_arr)
combine(gcd_value, max_value-min_value + 1)
