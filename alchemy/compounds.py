
class Compound():
	def __init__(self, 
		reactivity, # performs reactions before compounds of lower reactivity
		max_temp, # low = 1-2, mid = 3-4, high = 5-6; start at 3?
		tolerance, # steps after which being >max temp causes amount to go to 0
		cold_reactions=None, 
		warm_reactions=None, 
		hot_reactions=None):

		if (cold_reactions is None):
			cold_reactions = {}
		if (warm_reactions is None):
			warm_reactions = {}
		if (hot_reactions is None):
			hot_reactions = {}
		self.cold_reactions = cold_reactions
		self.warm_reactions = warm_reactions
		self.hot_reactions = hot_reactions
		self.reactivity = reactivity
		self.tolerance = tolerance
		self.max_temp = max_temp

# common in nature (12)
A = None
B = None
C = None
D = None
E = None
F = None
G = None
H = None
I = None
J = None
K = None
L = None

# rare in nature (6)
M = None
N = None
O = None
P = None
Q = None
R = None

# synthetic (6)
S = None
T = None
U = None
V = None
W = None
X = None

# synthetic and inert (2)
# no effect has these, they just worsen potency
Y = Compound(-1, 4, 2) # no reactivity, can degrade at high temp
Z = Compound(-1, 6, 10) # no reactivity, does not degrade