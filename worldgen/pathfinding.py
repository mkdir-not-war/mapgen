from math import exp
from numpy import dot
from operator import itemgetter

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

def manhattandist(a, b):
	result = abs(a[0] - b[0]) + abs(a[1] - b[1])
	return result

def h(start, goal):
	return manhattandist(start, goal)

def tupleequal(x, y):
	return x[0] == y[0] and x[1] == y[1]

def normallogistic(x):
	result = 1.0/(1.0 + exp(-1.0 * x))
	return result

def gravitycost(current, nextval):
	result = normallogistic(nextval - current)
	return result

def reconstruct_path(cameFrom, current):
	totalpath = [current] # include current position
	while current in cameFrom:
		current = cameFrom[current]
		totalpath.insert(0, current)
	return totalpath[:]

'''
mapobj.neighbors(pos) returns 
list of tuples that neighbor position pos

mapobj.size returns
size of tilemap
'''
def astar(start, goal, mapobj, *noisegrids):
	sumnoise = noisegrids[0]
	for n in noisegrids[1:]:
		sumnoise = sumnoise.add(n)

	startnoise = sumnoise.get(start[0], start[1])

	closedset = []
	openset = [start]
	camefrom = {}
	gScore = {}
	gScore[start] = 0
	fScore = {}
	fScore[start] = h(start, goal)

	while openset:
		currenti = 0
		for p in range(len(openset)):
			if (openset[p] in fScore):
				if (fScore[openset[p]] < currenti):
					currenti = p
		if tupleequal(openset[currenti], goal):
			return reconstruct_path(camefrom, openset[currenti])
		current = openset[currenti]
		openset = openset[:currenti] + openset[currenti+1:]
		closedset.append(current)

		for n in mapobj.neighbors(current):
			if n in closedset:
				continue
			if n not in gScore:
				gScore[n] = mapobj.size * 10
			cost_at_n = abs(sumnoise.get(n[0], n[1]) - startnoise)
			t_gScore = gScore[current] + cost_at_n
			if n not in openset:
				openset.append(n)
			elif t_gScore >= gScore[n]:
				continue
			camefrom[n] = current
			gScore[n] = t_gScore
			fScore[n] = t_gScore + h(n, goal)
	return False