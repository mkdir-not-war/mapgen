
class Compound():
	def __init__(self, 
		reactivity=-1, # performs reactions before compounds of lower reactivity
		max_temp=None, # low = 0-1, mid = 2-3, high = 4; start at 0
		tolerance=None, # steps after which being >max temp causes amount to go to 0
		cold_reactions=None, 
		warm_reactions=None, 
		hot_reactions=None):

		if (cold_reactions is None):
			cold_reactions = {}
		if (warm_reactions is None):
			warm_reactions = {}
		if (hot_reactions is None):
			hot_reactions = {}
		self.cold_reactions = cold_reactions.copy()
		self.warm_reactions = warm_reactions.copy()
		self.hot_reactions = hot_reactions.copy()
		self.reactivity = reactivity
		self.tolerance = tolerance
		self.max_temp = max_temp


allcompounds = {
	# +hp; tolerant at high; reacts with a lot
	'A' : Compound(
		reactivity=4, 
		max_temp=3, 
		tolerance=5, 
		cold_reactions={},
		warm_reactions={'H':'Z'}, 
		hot_reactions={}),
	'B' : Compound(
		reactivity=4, 
		max_temp=2, 
		tolerance=6,
		cold_reactions={'L':'Q'},
		warm_reactions={'H':'Z', 'L':'A'}, 
		hot_reactions={}),
	'C' : Compound(
		reactivity=4, 
		max_temp=None, 
		tolerance=None,
		cold_reactions={'L':'Q'},
		warm_reactions={}, 
		hot_reactions={}),
	'D' : Compound(
		reactivity=4, 
		max_temp=3, 
		tolerance=5, 
		cold_reactions={},
		warm_reactions={'H':'Z'}, 
		hot_reactions={}),
	'E' : None,
	'F' : None,
	'G' : None,
	# -hp; boils off; makes inert at warm temps with common stuff
	'H' : Compound(
		reactivity=2, 
		max_temp=2, 
		tolerance=3, 
		cold_reactions={},
		warm_reactions={'A':'Z', 'B':'Z', 'D':'Z'}, 
		hot_reactions={'N':'V', 'P':'V', 'Q':'V'}),
	'I' : None,
	'J' : None,
	'K' : None,
	# invis; boils off really early and quickly
	'L' : Compound(
		reactivity=2, 
		max_temp=1, 
		tolerance=2,
		cold_reactions={'C':'Q', 'B':'Q'},
		warm_reactions={'B':'A'}, 
		hot_reactions={}),

	### rare in nature (6) ###

	'M' : None,
	# in ectoplasm with L (invis); react with something synthetic to isolate L
	'N' : Compound(
		reactivity=1, 
		max_temp=3, 
		tolerance=2,
		cold_reactions={},
		warm_reactions={}, 
		hot_reactions={'H':'V'}),
	'O' : None,
	'P' : Compound(
		reactivity=1, 
		max_temp=3, 
		tolerance=2,
		cold_reactions={},
		warm_reactions={}, 
		hot_reactions={'H':'V'}),
	'Q' : Compound(
		reactivity=4, 
		max_temp=3, 
		tolerance=5,
		cold_reactions={},
		warm_reactions={}, 
		hot_reactions={'H':'V'}),
	'R' : None,

	### synthetic (6) ###

	'S' : None,
	'T' : None,
	'U' : None,
	# invis, heat; reactions to create this are only hot (H + P/Q -> V)
	'V' : None,
	'W' : None,
	'X' : None,

	### synthetic and inert (2) ###
	### no effect has these, they just worsen potency ###

	# no reactivity, can degrade at high temp
	'Y' : Compound(
		reactivity=-1, 
		max_temp=3, 
		tolerance=2),
	# no reactivity, does not degrade
	'Z' : Compound(
		reactivity=-1, 
		max_temp=None, 
		tolerance=None)
}
### common in nature (12) ###



def check_compound_reactions():
	for c in allcompounds:
		# while not finished...
		if (allcompounds[c] is None):
			continue
		# make sure each reaction is mirrored in the partner compound
		compound_info = allcompounds[c]
		for cr in compound_info.cold_reactions:
			result = compound_info.cold_reactions[cr]
			pairresult = None
			if (c in allcompounds[cr].cold_reactions):
				pairresult = allcompounds[cr].cold_reactions[c]
			if (pairresult is None or result != pairresult):
				print('%s + %s -> %s' % (c, cr, result))
				return False
		for wr in compound_info.warm_reactions:
			result = compound_info.warm_reactions[wr]
			pairresult = None
			if (c in allcompounds[wr].warm_reactions):
				pairresult = allcompounds[wr].warm_reactions[c]
			if (pairresult is None or result != pairresult):
				print('%s + %s -> %s' % (c, wr, result))
				return False
		for hr in compound_info.hot_reactions:
			result = compound_info.hot_reactions[hr]
			pairresult = None
			if (c in allcompounds[hr].hot_reactions):
				pairresult = allcompounds[hr].hot_reactions[c]
			if (pairresult is None or result != pairresult):
				print('%s + %s -> %s' % (c, hr, result))
				return False
	return True

if __name__=='__main__':
	print(check_compound_reactions())