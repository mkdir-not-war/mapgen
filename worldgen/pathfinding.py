def manhattandist(a, b):
	result = abs(a[0] - b[0]) + abs(a[1] - b[1])
	return result

def h(start, goal):
	return manhattandist(start, goal)

def tupleequal(x, y):
	return x[0] == y[0] and x[1] == y[1]

def noiseextremes(*noisegrids, mindist=1, buffer=1, minmax='max', num=1):
	assert(len(noisegrids) >= 1)

	sumnoise = noisegrids[0]
	for n in noisegrids[1:]:
		sumnoise = sumnoise.add(n)

	result = []
	sortednoise = []

	for y in range(sumnoise.size):
		for x in range(sumnoise.size):
			if (x+buffer < sumnoise.size and
				x-buffer >= 0 and
				y+buffer < sumnoise.size and
				y-buffer >= 0):
				sortednoise.append((sumnoise.get(x, y), (x, y)))

	sortednoise = sorted(sortednoise, key=lambda x: x[0], reverse=(minmax=='max'))

	#threshold = 0.8
	#sortednoise = filter(lambda x: x[0]/sumnoise.amplitude>=threshold, sortednoise)

	index = 0
	while (len(result) < num):
		val, pos = sortednoise[index]
		tooclose = False
		for pos2 in result:
			if manhattandist(pos, pos2) <= buffer or tooclose:
				tooclose = True
		if not tooclose:
			result.append(pos)
		index += 1

	return result


def reconstruct_path(cameFrom, current):
	totalpath = [] # don't include current position
	while current in cameFrom:
		current = cameFrom[current]
		totalpath.insert(0, current)
	return totalpath[1:]

def astar(start, goal, tilemap, *noisegrids):
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

		for n in neighbors(current, tilemap):
			if n in closedset:
				continue
			if n not in gScore:
				gScore[n] = len(tilemap) * 10
			cost_at_n = max(sumnoise.get(n[0], n[1]) - startnoise, 0.001)
			t_gScore = gScore[current] + cost_at_n
			if n not in openset:
				openset.append(n)
			elif t_gScore >= gScore[n]:
				continue
			camefrom[n] = current
			gScore[n] = t_gScore
			fScore[n] = t_gScore + h(n, goal)
	return False