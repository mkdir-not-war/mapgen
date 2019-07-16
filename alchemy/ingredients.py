from numpy import dot
from operator import itemgetter
import compounds
from effects import alleffects, effectvector

def squaredlen(vec):
	result = 0
	for d in vec:
		result += d ** 2
	return result

def angle_similarity(target, vecs):
	square_cos = {}
	sqlen_target = squaredlen(target)
	for v in vecs:
		dotprod = dot(v, target)
		value = (dotprod * dotprod) / (squaredlen(v) * sqlen_target)
		square_cos[v] = value
	return sorted(square_cos.items(), key=itemgetter(1), reverse=True)

def potency(compounds, signature):
	# mask out signature from compounds
	values = []
	for c in compounds:
		if c in signature:
			values.append(compounds[c])
	# find minimum value among masked compounds
	return min(values)

class Ingredient():
	def __init__(self, name, compounds, base=False):
		self.name = name
		self.compounds = compounds.copy() # {name : amount}
		self.effects = self.calculateeffects()

	def calculateeffects(self):
		result = [] # [(effect, potency), ...]
		compound_vector = [self.compounds[i] for i in sorted(self.compounds)]
		effect_vectors = [tuple(e.vector) for e in alleffects]
		effects_by_similarity = angle_similarity(
			tuple(compound_vector), effect_vectors)
		for e in effects_by_similarity:

			result.append()
		return result

	def printeffects(self):
		for effect, potency in self.effects:
			print("%s: %s" % (effect.stat, str(potency)))

# base = Ingredient
# steps = [(<action>, <ingredient>/None)]
def brew(base, steps):
	compounds = {}
	result = Ingredient("potion", compounds, base=True)
	return result

water = Ingredient("water", {}, base=True)
blood = Ingredient("blood", {}, base=True)
troll_bone = Ingredient("troll bone", {})
dragon_thistle = Ingredient("dragon thistle", {})
milk_weed = Ingredient("milk weed", {})