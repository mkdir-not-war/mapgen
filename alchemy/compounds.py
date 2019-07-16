
class Compound():
	def __init__(self, 
		reactivity,
		temp_range,
		tolerance,
		cold_reactions=None, 
		warm_reactions=None, 
		hot_reactions=None):
		if (cold_reactions is None):
			cold_reactions = {}
		if (warm_reactions is None):
			warm_reactions = {}
		if (hot_reactions is None):
			hot_reactions = {}
		self.cold_reactions
		self.warm_reactions
		self.hot_reactions
		self.reactivity
		self.tolerance = tolerance
		self.min_temp, self.max_temp = temp_range

# make one compound for each letter of the greek alphabet (24 letters)

# common in nature (10)
alphanine = None
betanine = None
gammanine = None
deltanine = None
epsilonine = None
zetanine = None
etanine = None
thetanine = None
iotanine = None
kappanine = None

# rare in nature (6)
lambdanine = None
munine = None
nunine = None
xinine = None
omicronine = None
pinine = None

# synthetic (6)
rhonine = None
sigmanine = None
taunine = None
upsilonine = None
phinine = None
chinine = None

# synthetic and inert (2)
# no effect has these, they just worsen potency
psinine = None
omeganine = None