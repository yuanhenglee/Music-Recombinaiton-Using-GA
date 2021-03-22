from Preprocess import ProcessedMIDI
from LBDM import LBDM

from mido import MidiFile


if __name__ == "__main__":

        mid = MidiFile("C:/Users/user/Documents/code/Music Recombination/midi_file/young.mid")

        period = ProcessedMIDI( mid)

        period.printPeriod()

        LBDM( period )