from zodb import ZODB, transaction
from Preprocess import ProcessedMIDI
import MusicSegmentation_2 as MusicSegmentation
from ILBDM import ILBDM
import Constant as C
from MusicTree import treeNode
from Individual import Individual

from mido import MidiFile

import os


def storeIntoDB(name):
    dbpath = './Music/'+name+'.fs'
    midipath = '../midi_file/'+name+'.mid'
    mid = MidiFile(midipath)
    parsedMIDI = ProcessedMIDI(mid)
    result_ILBDM = ILBDM(parsedMIDI)
    musicTree = treeNode(
        0, parsedMIDI.noteSeq[C.PITCHINDEX], parsedMIDI.noteSeq[C.DURATIONINDEX], result_ILBDM)
    cuttingPoint = MusicSegmentation.musicSegmentation2(
        parsedMIDI, result_ILBDM)
    signaturePossibilities = MusicSegmentation.extractSignatures(parsedMIDI)
    db = ZODB(dbpath)
    dbroot = db.dbroot

    for i, signature in enumerate(signaturePossibilities):
        dbroot[i] = Individual(parsedMIDI, cuttingPoint,
                               signaturePossibilities, signature, [musicTree])
    transaction.commit()
    db.close()


if __name__ == "__main__":

    import sys
    from mido import MidiFile
    from Preprocess import ProcessedMIDI

    name = sys.argv[1]
    if name == "all":
        from progress.bar import IncrementalBar
        path = os.path.join( os.path.dirname(__file__), '../midi_file')
        all_midi_files = [ f[:-4] for f in os.listdir(path) if f.endswith('.mid') ]
        n_midi_files = len(all_midi_files)
        with IncrementalBar('store to ZODB', max=n_midi_files) as bar:
            for i in range(n_midi_files):
                storeIntoDB(all_midi_files[i])
                bar.next()
        # directory = '../midi_file'
        # for filename in os.listdir(directory):
        #     print("|", end="")
        #     if filename.endswith(".mid"):
        #         storeIntoDB(filename[:-4])
        #     else:
        #         continue
    else:
        storeIntoDB(name)
