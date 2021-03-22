from Preprocess import ProcessedMIDI
from LBDM import LBDM

from mido import MidiFile

import csv
from pathlib import Path



if __name__ == "__main__":

    base_path = Path(__file__).parent
    file_path = (base_path / "../midi_file/young.mid").resolve()

    mid = MidiFile(file_path)

    period = ProcessedMIDI(mid)

    period.printPeriod()

    LBDM(period)
