

class Individual:
	def __init__( self, parsedMIDI, ancestorMIDI, signature ):
		self._parsedMIDI = parsedMIDI
		self._ancestorMIDI = ancestorMIDI
		self._signature = signature

		# ! TEST
		self.printIndividual()



	def printIndividual( self ):
		# OG MIDI
		self._parsedMIDI.printMIDI()
		print("Signature: \n", self._signature)
		# segmentation info


