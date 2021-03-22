from Preprocess import ProcessedMIDI
from LBDM import LBDM

from mido import MidiFile


if __name__ == "__main__":

<<<<<<< HEAD
        mid = MidiFile("../midi_file/young.mid")
=======
    mid = MidiFile("../midi_file/young.mid")
>>>>>>> 4b615c6c199504f329d3cd3beb63fb325b6814e2

    period = ProcessedMIDI(mid)

    period.printPeriod()

    LBDM(period)
