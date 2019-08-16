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
	'wall' : BuildingType('wall', 1, 1)
}

class MapObject():
	def __init__(self, name, x, y):
		self.position = (x, y)
		self.buildingtype = buildingtypes[name]

	def width(self):
		return self.buildingtype.width

	def height(self):
		return self.buildingtype.height

	def collide(self, x, y):
		result = (
			x >= self.position[0] and
			x < self.position[0] + self.w and
			y >= self.position[1] and
			y < self.position[1] + self.h)
		return result

MIN_NEXUS = 2
MAX_NEXUS = 7
NEX_TIER_RADIUS = 3
NEX_NUM_TIERS = 3
NEXUS_DIST = NEX_TIER_RADIUS * NEX_NUM_TIERS * 2
NEX_RADIUS = NEX_TIER_RADIUS * NEX_NUM_TIERS

class TownNexus():
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.next = {} # (direction) -> TownNexus
		self.buildings = {} # (directionvector) -> name

	def mappos(x, y, size):
		result = (
			size//2 + x*NEXUS_DIST, 
			size - 1 - (NEX_RADIUS + y*NEXUS_DIST))
		return result

class Town():
	def __init__(self, size, p):
		self.size = size # width (square)
		self.road_bitmap = [0] * size**2
		self.buildings = {} # (x, y) -> MapObject
		self.nexuses = {} # (nexx, nexy) -> TownNexus
		self.numnex = MIN_NEXUS + int(p * (MAX_NEXUS - MIN_NEXUS))

		self.gennexuses()
		self.genbuildings()
		self.genroads()

	def inbounds(self, x, y, buffer=0):
		result = (x-buffer >= 0 and
			x+buffer < self.size and
			y-buffer >= 0 and
			y+buffer < self.size)
		return result

	def gennexuses(self):
		newnexuses = []
		startpos = (0, 0)
		startnexus = TownNexus(*startpos)
		newnexuses.append(startnexus)
		self.nexuses[startpos] = startnexus
		numnexuses = 1

		possibledirs = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0)]

		while (numnexuses < self.numnex):
			for nex in newnexuses[::-1]:
				# pick a possible dir
				currentpos = (nex.x, nex.y)
				dirtocenter = [(0, 1)]
				if (nex.x != 0):
					dirtocenter.append((-1 * int(nex.x/abs(nex.x)), 1))
				newdir = choice(possibledirs+dirtocenter)
				newpos = (currentpos[0]+newdir[0], currentpos[1]+newdir[1])
				while (not self.inbounds(
					*TownNexus.mappos(newpos[0], newpos[1], self.size),
					buffer=NEX_RADIUS)):

					newdir = choice(possibledirs+dirtocenter)
					newpos = (currentpos[0]+newdir[0], currentpos[1]+newdir[1])
				if (newpos in self.nexuses):
					if (not newdir in nex.next):
						nex.next[newdir] = self.nexuses[newpos]
				elif (self.inbounds(
					*TownNexus.mappos(newpos[0], newpos[1], self.size))):

					newnex = TownNexus(*newpos)
					nex.next[newdir] = newnex
					newnexuses.append(newnex)
					self.nexuses[newpos] = newnex
					numnexuses += 1 
					if (numnexuses >= self.numnex):
						break

	def genbuildings(self):
		# for each nexus, in order of y-position
		# start at radius zero, determine if there is a well/fountain, etc
		# next distance, add shops
		# next distance (if no shops, same distance), add tavern and houses
		# next distance (if no tavern/houses, same again), add town hall, mansion and temples
		# finally, add guardhouses and a wall if there is one
		pass

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
					costmap[(i+x) + self.size * (y+j)] = self.size**2

		# from each nexus, get astar to connected nexuses
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

def printnexus(town):
	printlines = []
	for y in range(0, MAX_NEXUS):
		linelen = 3 * 2 * MAX_NEXUS
		printline = [' '] * linelen
		nextprintline = printline[:]
		for x in range(-1*MAX_NEXUS, MAX_NEXUS):
			if ((x, y) in town.nexuses):
				printline[MAX_NEXUS*3 + (x * 3) + 1] = '*'
				nex = town.nexuses[(x, y)]
				if (1, 0) in nex.next:
					printline[MAX_NEXUS*3 + (x * 3) + 2] = '>'
				if (-1, 0) in nex.next:
					printline[MAX_NEXUS*3 + (x * 3)] = '<'
				if (1, 1) in nex.next:
					nextprintline[MAX_NEXUS*3 + (x * 3) + 2] = '/'
				if (-1, 1) in nex.next:
					nextprintline[MAX_NEXUS*3 + (x * 3)] = '\\'
				if (0, 1) in nex.next:
					nextprintline[MAX_NEXUS*3 + (x * 3) + 1] = '^'
		printlines.append(printline)
		printlines.append(nextprintline)
	for line in printlines[::-1]:
		print(''.join(line))


def printtown(town):
	printmap = ['.' if i == 0 else '_' for i in town.road_bitmap]
	for x, y in town.buildings:
		building = town.buildings[(x, y)]
		for i in range(building.width):
			for j in range(building.height):
				if (
					i == 0 or 
					i == building.width or
					j == 0 or
					(j == building.height and i != building.width // 2)):
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
			print('seed: %d' % intseed)
		rand = random()
		town = Town(64, rand)
		printnexus(town)
		#printtown(town)
		print()

if __name__=='__main__':
	main()