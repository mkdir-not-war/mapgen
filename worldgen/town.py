from random import random, seed, randint, choice

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

	def collide(self, x, y):
		result = (
			x >= self.position[0] and
			x < self.position[0] + self.w and
			y >= self.position[1] and
			y < self.position[1] + self.h)
		return result

MIN_NEXUS = 2
MAX_NEXUS = 8

class TownNexus():
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.next = {} # (direction) -> TownNexus
		self.buildings = {} # (directionvector) -> name

class Town():
	def __init__(self, size, p):
		self.size = size # width (square)
		self.road_bitmap = [0] * size**2
		self.buildings = {} # (x, y) -> MapObject
		self.nexuses = {} # (nexx, nexy) -> TownNexus
		self.numnex = MIN_NEXUS + int(p * (MAX_NEXUS - MIN_NEXUS))

		self.gennexuses()
		self.genbuildings()

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
				if (newpos in self.nexuses):
					if (not newdir in nex.next):
						nex.next[newdir] = self.nexuses[newpos]
				else:
					newtown = TownNexus(*newpos)
					nex.next[newdir] = newtown
					newnexuses.append(newtown)
					self.nexuses[newpos] = newtown
					numnexuses += 1 
					if (numnexuses >= self.numnex):
						break

	def genbuildings(self):
		pass

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
		print()

if __name__=='__main__':
	main()