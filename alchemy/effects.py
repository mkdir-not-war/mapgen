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

	def effectvector(self):
		result = [1 if i in self.signature else 0 for i in compound_names]
		return result

alleffects = {
	'+hp' : Effect('+hp', 					['A', 'D', 'M']),
	'+stamina' : Effect('+stamina', 		['A', 'B', 'O']),
	'+speed' : Effect('+speed', 			['C', 'O', 'S']),
	'+defense' : Effect('+defense', 		['A', 'M', 'T']),
	'+spdefense' : Effect('+spdefense', 	['E', 'G', 'N']),
	'+attack' : Effect('+attack', 			['B', 'F', 'W']),
	'+spattack' : Effect('+spattack', 		['E', 'K', 'X']),
	'+heat' : Effect('+heat', 				['A', 'U', 'V']),

	'-hp' : Effect('-hp', 					['E', 'H', 'P']),
	'-stamina' : Effect('-stamina', 		['F', 'J', 'R']),
	'-speed' : Effect('-speed', 			['D', 'I', 'N']),
	#'-defense' : Effect('-defense', 		['A', 'M', 'T']),
	#'-spdefense' : Effect('-spdefense', 	['E', 'G', 'N']),
	'-attack' : Effect('-attack', 			['H', 'I', 'S']),
	#'-spattack' : Effect('-spattack', 		['C', 'O', 'S']),
	'-heat' : Effect('-heat', 				['B', 'Q', 'X']),
	'invisibility' : Effect('invisibility', ['L', 'V', 'X'])
}
	