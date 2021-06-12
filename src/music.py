from Preprocess import ProcessedMIDI
import MusicSegmentation_2 as MusicSegmentation
from ILBDM import ILBDM

from mido import MidiFile


class Music:
    def __init__(self, path, _name):
        self.name = _name
        self.mid = MidiFile(path)
        self.parsedMIDI = ProcessedMIDI(self.mid)
        self.result_ILBDM = ILBDM(self.parsedMIDI)
        self.cuttingPoint = MusicSegmentation.musicSegmentation2(
            self.parsedMIDI, self.result_ILBDM)
        self.signaturePossibilities = MusicSegmentation.extractSignatures(
            self.parsedMIDI)
