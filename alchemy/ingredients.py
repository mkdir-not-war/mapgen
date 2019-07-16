from numpy import dot
from operator import itemgetter
import compounds
from effects import alleffects
from string import ascii_uppercase as compound_names

def squaredlen(vec):
	result = 0
	for d in vec:
		result += d ** 2
	return result

def effect_ingredient_similarity(target, size):
	square_cos = {}
	sqlen_target = squaredlen(target)
	for e in alleffects.values():
		effect_vector = tuple(e.vector)
		dotprod = dot(effect_vector, target)
		value = (dotprod * dotprod) / \
			(squaredlen(effect_vector) * sqlen_target)
		if (not value in square_cos):
			square_cos[value] = [e]
		else:
			square_cos[value].append(e)

	scores_nodup = sorted(square_cos, reverse=True)
	scores = []
	for s in scores_nodup:
		for i in range(len(square_cos[s])):
			scores.append(s)
	effects = []
	for s in scores_nodup:
		effects.extend(square_cos[s])
	return scores[:size], effects[:size]

def potency(compounds, signature):
	# mask out signature from compounds
	values = []
	for c in compounds:
		if c in signature:
			values.append(compounds[c])
	# find minimum value among masked compounds
	if not values:
		return 0
	return min(values)

class Ingredient():
	def __init__(self, name, compounds, crushed=None, base=False):
		self.name = name
		self.compounds = compounds.copy() # {name : amount}
		self.effects = self.calculateeffects()
		self.crushed = crushed
		self.base = base

	def calculateeffects(self):
		result = {} # [(effect, potency), ...]
		compound_vector = [self.compounds[i] 
							if i in self.compounds.keys() else 0 
							for i in list(compound_names)]	
		scores, effects = effect_ingredient_similarity(
			tuple(compound_vector), 3)
		for e_index in range(len(effects)):
			effect = effects[e_index]
			compound_potency = potency(self.compounds, effect.signature)
			effect_potency = int(max((10.0 * (compound_potency) * \
				scores[e_index]), 0))
			if (effect_potency > 0):
				result[effect.stat] = [effect, effect_potency]

		return result

	def crush(self):
		result = ingredients[self.crushed]
		return result

	def printeffects(self):
		for effect, potency in self.effects.values():
			print("%s: %s" % (effect.stat, str(potency)))

# base = Ingredient
# steps = [(<action>, <ingredient>/None)]
def brew(base, steps):
	compounds = {}
	result = Ingredient("potion", compounds, base=True)
	return result

ingredients = {
	'water' : Ingredient("water", {'A':1, 'B':1, 'C':1, 'D':1}, base=True),
	'blood' : Ingredient("blood", {'D':2, 'E':2, 'G':1, 'H':1}, base=True),
	'bone' : Ingredient("bone", {'A':1, 'E':1}, crushed="crushed bone"),
	'crushed bone' : Ingredient("crushed bone", {'A':1, 'E':1, 'M':1}),
	'drake thistle' : Ingredient("drake thistle", {'C':1, 'E':1, 'G':1, 'H':2}),
	'milkweed' : Ingredient("milkweed", {'C':1, 'F':1, 'H':2, 'O':1})
}

if __name__=='__main__':
	for i in ingredients:
		print('~', i, '~')
		ingredients[i].printeffects()
		print('-'*12)
