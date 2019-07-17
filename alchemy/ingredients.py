from numpy import dot
from operator import itemgetter
import compounds
from effects import alleffects, EffectType
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
		self.effects = self.calculateeffects(compounds)
		self.base = base

		if crushed is None:
			crushed = self.name
		self.crushed = crushed

		if len(name) >= 6 and name[-6:] == "potion":
			self.name = self.namepotion(name)


	def calculateeffects(self, compounds):
		max_effects_per_ingredient = 3
		result = {} # [(effect, potency), ...]
		compound_vector = [compounds[i] 
							if i in compounds.keys() else 0 
							for i in list(compound_names)]	
		scores, effects = effect_ingredient_similarity(
			tuple(compound_vector), max_effects_per_ingredient)
		for e_index in range(len(effects)):
			effect = effects[e_index]
			compound_potency = potency(compounds, effect.signature)
			effect_potency = int(max((10.0 * (compound_potency) * \
				scores[e_index]), 0))
			if (effect.effecttype == EffectType.NEGATIVE):
				effect_potency *= -1
			# sum up negative and positive effects
			if (effect_potency != 0):
				if (effect.stat in result):
					result[effect.stat][1] += effect_potency
					if (result[effect.stat][1]) == 0:
						del result[effect.stat]
				else:
					result[effect.stat] = [effect, effect_potency]
		return result

	def namepotion(self, basename):
		effectslist = sorted(
			list(self.effects.items()),
			key=lambda e: e[1][1],
			reverse=True)
		if (len(effectslist) == 0):
			return 'inert potion of %s' % basename[:-7]
		max_pos_effects = []
		min_neg_effects = []
		max_potency = 0
		min_potency = 0
		for e in effectslist:
			potency = e[1][1]
			if potency > max_potency:
				max_potency = potency
				max_pos_effects = [e[0]]
			elif potency == max_potency:
				max_pos_effects.append(e[0])
			if potency < min_potency:
				min_potency = potency
				min_neg_effects = [e[0]]
			elif potency == min_potency:
				min_neg_effects.append(e[0])

		if (abs(min_potency) > max_potency):
			basename = basename[:-6] + 'poison'
			name = '%s of deplete %s' % (basename, ' and '.join(min_neg_effects))
		else:
			name = '%s of augment %s' % (basename, ' and '.join(max_pos_effects))

		return name

	def crush(self):
		result = ingredients[self.crushed]
		return result

	def printeffects(self):
		for effect, potency in self.effects.values():
			print("%s: %s" % (effect.stat, str(potency)))

# base = Ingredient
# steps = [(<action>, <ingredient>/None)]
def brew(base, steps):
	compounds = base.effects.copy()
	result = Ingredient("%s potion" % base.name, compounds, base=True)
	return result

ingredients = {
	# bases
	'water' : Ingredient("water", {'A':1, 'B':1, 'C':1, 'D':1}, base=True),
	'blood' : Ingredient("blood", {'D':2, 'E':2, 'G':1, 'H':1}, base=True),
	'slime' : Ingredient("slime", {'H':1, 'I':1, 'K':2, 'S':1}, base=True),
	'ectoplasm' : Ingredient("ectoplasm", {'H':1, 'I':1, 'L':2, 'N': 2}, base=True),
	# from corpses
	'bone' : Ingredient("bone", {'A':1, 'E':1}, crushed="crushed bone"),
	'crushed bone' : Ingredient("crushed bone", {'A':1, 'E':1, 'M':1}),
	'troll eye' : Ingredient("troll eye", {'F':2, 'H':1, 'I':1, 'K':1}, crushed="slime"), 
	'orc ear' : Ingredient("orc ear", {'F':1, 'G':1, 'J':1}, crushed="blood"),
	# plants
	'drake thistle' : Ingredient("drake thistle", {'C':1, 'E':1, 'G':1, 'H':2}),
	'milkweed' : Ingredient("milkweed", {'C':1, 'F':1, 'H':2, 'O':1})
}

bases = {k:v for (k,v) in ingredients.items() if v.base}

if __name__=='__main__':
	'''
	for i in ingredients:
		print('~', i, '~')
		ingredients[i].printeffects()
		print('-'*12)
	'''

	test_pot = Ingredient('test potion', {'F':2, 'B':3, 'Q':2, 'X':1}, base=True)
	print(test_pot.name)
	test_pot.printeffects()
