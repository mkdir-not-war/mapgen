from numpy import dot
from operator import itemgetter

class Potion():
	def __init__(self):
		self.effects = {} # <effected stat> : <value/change>

	def printpot(self):
		for effect in self.effects:
			print("%s: %s" % (effect, self.effects[effect]))

# base = Ingredient
# steps = [(<action>, <ingredient>/None)]
def brew(base, steps):
	result = Potions()
	return result

class Compound():
	def __init__(self):
		pass

class Ingredient():
	def __init__(self):
		pass

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

def parseinput(userinput):
	if userinput == 'help':
		print('help!')
	elif userinput == 'quit':
		exit(1)

def main():
	potions = []
	while(1):
		userinput = input('>> ')
		parseinput(userinput)

if __name__=='__main__':
	main()