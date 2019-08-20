from random import random, seed, randint, choice
from pathfinding import basicastar, manhattandist

class BuildingType():
	def __init__(self, name, w, h):
		self.name = name
		self.width = w
		self.height = h

buildingtypes = {
	'well' : BuildingType('well', 2, 2),
	'house' : BuildingType('house', 4, 4),
	'tavern' : BuildingType('tavern', 5, 4),
	'shop' : BuildingType('shop', 4, 4),
	'temple' : BuildingType('temple', 5, 6),
	'hall' : BuildingType('hall', 6, 4),
	'guardhouse' : BuildingType('guardhouse', 4, 4),
	'wall' : BuildingType('wall', 1, 2)
}

'''
0 - center
3 - up
evens - left, top to bottom
odds - right, top to bottom
'''

layoutoffsets = {
	0: (0, 0), 
	1: (1, 0), 
	2: (-1, 0), 
	3: (0, -1), 
	4: (-1, 1), 
	5: (1, 1), 
	6: (-1, 2), 
	7: (1, 2)
}

nexuslayouts = {
	'residential': {
		0: ['well'],
		1: ['house'],
		2: ['shop', 'house'],
		3: ['shop', 'house', 'temple', 'mansion'],
		4: ['house'], 
		5: ['house'],
		6: ['shop'],
		7: ['shop', 'house']
	},
	'commercial': {
		0 : [],
		1: ['shop'],
		2: ['shop', 'house'],
		3: ['shop', 'house', 'tavern'],
		4: ['shop'], 
		5: ['shop', 'house'],
		6: ['shop'],
		7: ['shop', 'house']
	}
}

class MapObject():
	def __init__(self, name, x, y):
		self.position = (x, y)
		self.buildingtype = buildingtypes[name]

	def width(self):
		return self.buildingtype.width

	def height(self):
		return self.buildingtype.height

	def rect(self):
		result = (
			self.position[0], self.position[1],
			self.buildingtype.width, self.buildingtype.height)
		return result

	def collide(self, x, y):
		return collide(x, y, self.rect())

def collide(x, y, rect):
	result = (
		x >= rect[0] and
		x < rect[0] + rect[2] and
		y >= rect[1] and
		y < rect[1] + rect[3])
	return result

def collide_rect(rec1, rect2, buffer=1):
	combined_rect = (
		rect1[0]-(rect2[2]+buffer),
		rect1[1]-(rect2[3]+buffer),
		rect1[2]+(rect2[2]+buffer*2),
		rect1[3]+(rect2[3]+buffer*2))
	result = self.collide(rect2[0], rect2[1], combrect)
	return result

MAX_NEXUS = 3
MIN_NEXUS = 1

NEXUS_X_OFFSET = 3
NEXUS_Y_BUFFER = 2

class TownNexus():
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.buildings = {} # (directionvector, tier) -> name

	def mappos(x, y, size):
		result = (
			size//2 + x*NEXUS_DIST, 
			size - 1 - (NEX_RADIUS + y*NEXUS_DIST))
		return result

class Town():
	def __init__(self, size, p, water=[]):
		self.size = size # width (square)
		self.road_bitmap = [0] * size**2
		self.buildings = {} # (x, y) -> MapObject
		self.minimap = {} # (x, y) -> building name
		self.p = p
		self.water = water # list of directions

		self.genminimap()
		#self.genbuildings()
		#self.genroads()

	def inbounds(self, x, y, buffer=0):
		result = (x-buffer >= 0 and
			x+buffer < self.size and
			y-buffer >= 0 and
			y+buffer < self.size)
		return result

	def coastbox(self, waterdir, size, buffer):
		w = size-1
		h = size-1
		d = buffer

		# return x, y, w, h

		if (waterdir == (1,0)):
			return (w-d, 0, d, h)
		elif (waterdir == (0, -1)):
			return (0, 0, d, h)

		elif (waterdir == (0, 1)):
			return (0, h-d, w, d)
		elif (waterdir == (-1, 0)):
			return (0, 0, w, d)
		
		elif (waterdir == (1, 1)):
			return (w-d, h-d, d, d)
		elif (waterdir == (-1, 1)):
			return (0, h-d, d, d)
		elif (waterdir == (1, -1)):
			return (w-d, 0, d, d)
		elif (waterdir == (-1, -1)):
			return (0, 0, d, d)

	def genminimap(self):
		minimapwidth = self.size // 7
		center = (minimapwidth-1) // 2

		walled = False
		if self.p < 0.5:
			walled = True

		nexuses = []
		numnex = randint(MIN_NEXUS, MAX_NEXUS)

		# first nexus in center column
		nexx = center
		nexy = randint(center-NEXUS_Y_BUFFER, center+NEXUS_Y_BUFFER)
		nexuses.append((nexx, nexy))

		if (numnex > 1):
			nexx = center - NEXUS_X_OFFSET
			nexy = randint(NEXUS_Y_BUFFER, minimapwidth-NEXUS_Y_BUFFER)
			nexuses.append((nexx, nexy))
		if (numnex > 2):
			nexx = center + NEXUS_X_OFFSET
			nexy = randint(NEXUS_Y_BUFFER, minimapwidth-NEXUS_Y_BUFFER)
			nexuses.append((nexx, nexy))

		# enclose in walls if walled
		if walled:
			for x in range(minimapwidth):
				for y in range(minimapwidth):
					if (
						x == 0 or 
						x == minimapwidth-1 or
						y == 0 or
						y == minimapwidth-1):

						self.minimap[(x, y)] = 'wall'

		# place buildings around nexus
		for nexx, nexy in nexuses:
			nexustype = choice(['residential', 'commercial'])
			numbuildings = randint(3, 8)
			for i in range(numbuildings):
				offset = layoutoffsets[i]
				buildingchoices = nexuslayouts[nexustype][i]
				posx, posy = nexx + offset[0], nexy + offset[1]
				if ((posx, posy) in self.minimap and 
					self.minimap[(posx, posy)] == 'wall'):
					if posy < minimapwidth-1 and random() < 0.4:
						self.minimap[(posx, posy)] = 'guardhouse'
				elif (len(buildingchoices) > 0):
					building = choice(buildingchoices)
					if (i == 0 and random() > 0.2):
						continue
					else:
						self.minimap[(posx, posy)] = building

		# scoot walls in closer to buildings
		if walled:
			leftbound = 0
			for x in range(1, center):
				hasbuilding = False
				for y in range(minimapwidth):
					if (x, y) in self.minimap and self.minimap[(x, y)] != 'wall':
						hasbuilding = True
				if not hasbuilding:
					leftbound = x
			if leftbound > 0:
				leftbound = leftbound-1
				for x in range(leftbound):
					self.minimap.pop((x, 0), None)
					self.minimap.pop((x, minimapwidth-1), None)
				for y in range(minimapwidth):
					self.minimap.pop((0, y), None)
					self.minimap[leftbound, y] = 'wall'

			rightbound = minimapwidth-1
			for x in list(range(center, minimapwidth))[::-1]:
				hasbuilding = False
				for y in range(minimapwidth):
					if (x, y) in self.minimap and self.minimap[(x, y)] != 'wall':
						hasbuilding = True
				if not hasbuilding:
					rightbound = x
			if rightbound < minimapwidth-1:
				rightbound = rightbound+1
				for x in range(rightbound, minimapwidth):
					self.minimap.pop((x, 0), None)
					self.minimap.pop((x, minimapwidth-1), None)
				for y in range(minimapwidth):
					self.minimap.pop((minimapwidth-1, y), None)
					self.minimap[rightbound, y] = 'wall'

			topbound = 0
			for y in range(0, center):
				hasbuilding = False
				for x in range(minimapwidth):
					if (x, y) in self.minimap and self.minimap[(x, y)] != 'wall':
						hasbuilding = True
				if not hasbuilding:
					topbound = y
			if topbound > 0:
				topbound = topbound-1
				for y in range(topbound):
					self.minimap.pop((leftbound, y), None)
					self.minimap.pop((rightbound, y), None)
				for x in range(leftbound, rightbound):
					self.minimap.pop((x, 0), None)
					self.minimap[x, topbound] = 'wall'

		# delete walls in directions of water
		for waterdir in self.water:
			cb = self.coastbox(waterdir, minimapwidth, 1)
			for y in range(cb[1], cb[1]+cb[3]):
				for x in range(cb[0], cb[0]+cb[2]):
					self.minimap.pop((x, y), None)


	def genbuildings(self):
		minimapwidth = self.size // 7
		for bx, by in self.minimap:
			bname = self.minimap[(bx, by)]

			x = bx * minimapwidth
			if bname == 'wall' and bx == minimapwidth-1:
				x = minimapwidth**2 - 1

			if bname != 'wall':
				self.buildings[(x, y)] = MapObject(bname, x, y)


	def getroadoutlets(self):
		result = []
		return result

	def neighbors(self, pos):
		return self.adjacenttiles(pos[0], pos[1], True)

	def adjacenttiles(self, x, y, diag=False):
		result = []

		xplus = x+1
		xminus = x-1
		if (xminus < 0):
			xminus = None
		if (xplus >= self.size):
			xplus = None

		yplus = y+1
		yminus = y-1
		if (yminus < 0):
			yminus = None
		if (yplus >= self.size):
			yplus = None

		if (not xplus is None):
			result.append((xplus, y))
		if (not xminus is None):
			result.append((xminus, y))
		if (not yplus is None):
			result.append((x, yplus))
		if (not yminus is None):
			result.append((x, yminus))

		if (diag):
			if (not yplus is None):
				if (not xplus is None):
					result.append((xplus, yplus))
				if (not xminus is None):
					result.append((xminus, yplus))
			if (not yminus is None):
				if (not xplus is None):
					result.append((xplus, yminus))
				if (not xminus is None):
					result.append((xminus, yminus))

		return result

	def genroads(self):
		# get cost map (1 = ground, size**2 = wall/building)
		costmap = [1] * self.size**2
		for x, y in self.buildings:
			building = self.buildings[(x, y)]
			for j in range(building.height()):
				for i in range(building.width()):
					try:
						costmap[(i+x) + self.size * (y+j)] = self.size**2
					except:
						print(x, y)
						print((i+x, y+j), self.size)
						input()

		# from each nexus, get astar to connected nexuses
		'''
		paths = []
		for nexpos in self.nexuses:
			nex = self.nexuses[nexpos]
			for relnext in nex.next:
				nextx, nexty = nexpos[0]+relnext[0], nexpos[1]+relnext[1]
				pos1 = TownNexus.mappos(nexpos[0], nexpos[1], self.size)
				pos2 = TownNexus.mappos(nextx, nexty, self.size)
				paths.append(basicastar(pos1, pos2, self, costmap))

			# if exit road from nexus, connect to the nearest of the road outlets
			if False:
				outlets = self.getroadoutlets()
				closestoutlet = None
				mindist = self.size**2
				for outlet in outlets:
					dist = manhattandist(outlet)
					if dist < mindist:
						closestoutlet = outlet
						mindist = dist
				nexpos = TownNexus.mappos(nex.x, nex.y, self.size)
				paths.append(
					basicastar(nexpos, closestoutlet, self, costmap))
		'''

		# draw paths, overlapping is ok
		for path in paths:
			if (path == False):
				continue
			for x, y in path:
				self.road_bitmap[x + self.size * y] = 1

		# expand road
		# copy map, for each tile, if adjacent to non-road, set to road
		copymap = self.road_bitmap[:]
		for y in range(self.size):
			for x in range(self.size):
				if self.road_bitmap[x + self.size * y] == 1:
					adjtiles = self.adjacenttiles(x, y, True) # not diagonal
					for adjx, adjy in adjtiles:
						if self.road_bitmap[adjx + self.size * adjy] == 0:
							copymap[adjx + self.size * adjy] = 1

		self.road_bitmap = copymap[:]

		# for each building, draw a line of road bordering its south wall
		for x, y in self.buildings:
			building = self.buildings[(x, y)]
			southwally = building.height() + y
			for i in range(building.width()):
				roadpos = (i+x, southwally)
				if self.inbounds(*roadpos):
					self.road_bitmap[roadpos[0] + self.size * roadpos[1]] = 1

def printminimap(town):
	minimapwidth = town.size // 7
	for y in range(minimapwidth):
		printline = []
		for x in range(minimapwidth):
			if (x, y) in town.minimap:
				printline.append(town.minimap[(x, y)][0])
			else:
				printline.append('.')
		print(''.join(printline))
	print()

def printtown(town):
	printmap = ['.' if i == 0 else '_' for i in town.road_bitmap]
	for x, y in town.buildings:
		building = town.buildings[(x, y)]
		for i in range(building.width()):
			for j in range(building.height()):
				if (
					i == 0 or 
					i == building.width()-1 or
					j == 0 or
					(j == building.height()-1 and 
						i != building.width() // 2 and 
						building.buildingtype.name != 'well')):
					printmap[(x+i) + town.size * (y+j)] = '#'
				else:
					printmap[(x+i) + town.size * (y+j)] = ' '
	for y in range(town.size):
		print(''.join(printmap[y*town.size:(y+1)*town.size]))
		
def main():
	while(1):
		rawseed = input("seed: ")
		intseed = randint(1, 2**15)
		try:
			intseed = int(rawseed)
			seed(intseed)
		except:
			seed(intseed)
			print('seed: %d' % intseed)
		rand = random()
		town = Town(64, rand)
		printminimap(town)
		#printtown(town)
		print()

if __name__=='__main__':
	main()