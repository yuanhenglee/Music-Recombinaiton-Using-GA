from Preprocess import ProcessedMIDI
from LBDM import LBDM

from mido import MidiFile


if __name__ == "__main__":

        mid = MidiFile("../midi_file/young.mid")

        period = ProcessedMIDI( mid)

        period.printPeriod()

        LBDM( period )