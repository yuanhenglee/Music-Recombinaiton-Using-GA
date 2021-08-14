from mido import MidiFile, Message, MidiTrack
from Utility import

def parsed2MIDI( parsedMIDI ):
    minLengthInTicks = parsedMIDI.minLengthInTicks


if __name__ == '__main__':
    mid = MidiFile( )
    track = MidiTrack( )

    track.append(Message('program_change', program=12, time=0))
    track.append(Message('note_on', note=64, velocity=64, time=1024))
    track.append(Message('note_off', note=64, velocity=127, time=1024))
    track.append(Message('note_on', note=65, velocity=64, time=1024))
    track.append(Message('note_off', note=65, velocity=127, time=1024))
    track.append(Message('note_on', note=66, velocity=64, time=1024))
    track.append(Message('note_off', note=66, velocity=127, time=1024))
    track.append(Message('note_on', note=67, velocity=64, time=1024))
    track.append(Message('note_off', note=67, velocity=127, time=1024))
    mid.tracks.append( track )

    mid.save('new_song.mid')