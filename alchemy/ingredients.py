from numpy import dot
from operator import itemgetter
import compounds

def squaredlen(vec):
	result = 0
	for d in vec:
		result += d ** 2
	return result

def vectorsbyclosestangle(target, vecs):
	square_cos = {}
	sqlen_target = squaredlen(target)
	for v in vecs:
		dotprod = dot(v, target)
		value = (dotprod * dotprod) / (squaredlen(v) * sqlen_target)
		square_cos[v] = value
	return max(square_cos.items(), key=itemgetter(1))

class Ingredient():
	def __init__(self, name, compounds, base=False):
		self.name = name
		self.compounds = compounds.copy() # dict
		self.effects = calculateeffects()

	def calculateeffects(self):
		result = [] # [(effect, potency), ...]
		return result

	def printeffects(self):
		for effect, potency in self.effects:
			print("%s: %s" % (effect.stat, str(potency)))

# base = Ingredient
# steps = [(<action>, <ingredient>/None)]
def brew(base, steps):
	result = Ingredient("potion", [], base=True)
	return result

water = Ingredient("water", [], base=True)
blood = Ingredient("blood", [], base=True)
troll_bone = Ingredient("troll bone", [])
dragon_thistle = Ingredient("dragon thistle", [])
milk_weed = Ingredient("milk weed", [])