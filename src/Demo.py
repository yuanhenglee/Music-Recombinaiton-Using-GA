from mido import MidiFile, Message, MidiTrack, MetaMessage
from Utility import pitch2MIDIPitch
import Constant as C

def parsed2MIDI( parsedMIDI ):
    minLengthInTicks = parsedMIDI.minLengthInTicks
    durationSeq = parsedMIDI.noteSeq[C.DURATIONINDEX]
    pitchSeq = parsedMIDI.noteSeq[C.PITCHINDEX]

    mid = MidiFile( ticks_per_beat = parsedMIDI.ticks_per_beat)
    track = MidiTrack( )

    track.append(Message('program_change', program=0, time=0))
    track.append(MetaMessage('set_tempo', tempo=parsedMIDI.tempo, time=0))

    deltaTime = 1000 # tmp need reconsider
    for i in range( parsedMIDI.numberOfNotes ):
        if pitchSeq[i] != 0:
            track.append(Message('note_on', note=pitch2MIDIPitch(pitchSeq[i]), time=deltaTime))
            deltaTime = int(durationSeq[i] * minLengthInTicks)
            track.append(Message('note_off', note=pitch2MIDIPitch(pitchSeq[i]), time=deltaTime))
            deltaTime = 0
        else:
            deltaTime = int(durationSeq[i] * minLengthInTicks)

    mid.tracks.append( track )
    mid.save('new_song.mid')


if __name__ == '__main__':
    import sys
    from Preprocess import ProcessedMIDI
    path = sys.argv[1]
    mid = MidiFile(path)
    parsedMIDI = ProcessedMIDI(mid)
    print( parsedMIDI.tempo)
    parsed2MIDI( parsedMIDI )