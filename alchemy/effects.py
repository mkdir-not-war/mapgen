from string import ascii_uppercase as compound_names

class Effect():
	def __init__(self, stat, signature):
		self.stat = stat
		'''
		Each effect's signature is 3 compounds (names), 
		and implies equal amounts of each. Basically a bit-
		vector with exactly three 1's.

		Effects that have only compounds that occur in nature means
		eating raw ingredients can potentially yield that effect
		with high potency.
		'''
		self.signature = signature
		self.vector = self.effectvector()

	def effectvector():
		result = [1 if i in self.signature else 0 for i in compound_names]
		return result

alleffects = [
	Effect('hp', ['A', 'D', 'M']),
	Effect('stamina', ['A', 'B', 'O']),
	Effect('speed', ['C', 'O', 'S']),
	Effect('defense', ['A', 'M', 'T'])
]