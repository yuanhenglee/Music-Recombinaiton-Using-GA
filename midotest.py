from mido import MidiFile
from math import gcd

mid = MidiFile('bee.mid')
gcd_value = 0
min_value = 109
max_value = 20
note_list = []


def findMaxMin(note):
    global max_value, min_value
    if note > max_value:
        max_value = note
    if note < min_value:
        min_value = note


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
            if note_list != [] and msg.time != 0:
                for i in range((int)(msg.time / gcd_value)):
                    note_list.append(0)
        elif msg.type == 'note_off':
            # 紀錄音
            for i in range((int)(msg.time / gcd_value)):
                if i != 0:
                    note_list.append(max_value - min_value + 1 + 1)
                else:
                    note_list.append(msg.note - min_value + 1)

print(note_list)
