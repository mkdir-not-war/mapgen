from operator import itemgetter
from numpy import dot
from enum import Enum
from random import choice
import entity as entityfuncs

possible_moves = [(0, 1), (1, 0), (-1, 0), (0, -1)]

class AIStates(Enum):
	IDLE = 1
	FOLLOWING = 2
	SEARCHING = 3

def manhattandist(a, b):
	result = abs(a[0] - b[0]) + abs(a[1] - b[1])
	return result

def h(start, goal):
	return manhattandist(start, goal)

def tupleequal(x, y):
	return x[0] == y[0] and x[1] == y[1]

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

# only cardinal directions
def neighbors(p, worldmap, travonly=True, buffer=1):
	x = p[0]
	y = p[1]
	result = []
	if (x - 1 >= buffer):
		if (not travonly or not worldmap.tileblocked(x-1, y)):
			result.append(tuple([x-1, y]))
	if (x + 1 < worldmap.width - buffer):
		if (not travonly or not worldmap.tileblocked(x+1, y)):
			result.append(tuple([x+1, y]))
	if (y - 1 >= buffer):
		if (not travonly or not worldmap.tileblocked(x, y-1)):
			result.append(tuple([x, y-1]))
	if (y + 1 < worldmap.height - buffer):
		if (not travonly or not worldmap.tileblocked(x, y+1)):
			result.append(tuple([x, y+1]))
	return result

def reconstruct_path(cameFrom, current):
	totalpath = [] # don't include current position
	while current in cameFrom:
		current = cameFrom[current]
		totalpath.insert(0, current)
	return totalpath[1:]

def astar(start, goal, worldmap, buffer=1, travonly=True, costs=True):
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

		for n in neighbors(current, worldmap, travonly=travonly, buffer=buffer):
			if n in closedset:
				continue
			if n not in gScore:
				gScore[n] = worldmap.size * 10
			# only actually keep track of costs if explicitly asked to
			if (costs):
				cost_at_n = worldmap.getcost(n[0], n[1], wallszero=travonly)
				t_gScore = gScore[current] + cost_at_n
			else:
				t_gScore = gScore[current] + 1
			##########################################################
			if n not in openset:
				openset.append(n)
			elif t_gScore >= gScore[n]:
				continue
			camefrom[n] = current
			gScore[n] = t_gScore
			fScore[n] = t_gScore + h(n, goal)
	return False
