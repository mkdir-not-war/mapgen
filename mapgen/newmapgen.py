import random
from math import sqrt
from tile import Tile
from biome import biomes
from ai import astar
from door import Door
from entity import Entity

wall = Tile('wall', True)
ground = Tile('ground', False)
water = Tile('water', True, False, cost=6)
tree = Tile('tree', False, True, cost=3)

printtile = {
        'wall' : '#',
        'ground' : '.',
        'water' : '~',
        'tree' : 'F'
}

min_monsters_per_room = 0
max_monsters_per_room = 12

class GameMap:
	def __init__(self, width, height, floor):
		self.width = width
		self.height = height
		self.size = width * height
		self.floor = floor
		self.tiles = self.initialize_tiles() # set in generate

		# set exits in generate
		self.exits = {}
		self.exits['north'] = None
		self.exits['south'] = None
		self.exits['west'] = None
		self.exits['east'] = None

		# includes corpses as well as live monsters
		self.monsters = None

		self.items = []

		self.biomename = None
		self.costmap = [] # set in generate

	def initialize_tiles(self):
		tiles = [Tile('wall', True) for tile in range(self.size)]
		return tiles

	def tileblocked(self, x, y):
		if (not self.inbounds(x, y) or 
			self.tiles[x + self.width * y].blocked):
			return True
		return False

	def tilename(self, x, y):
		return self.tiles[x + self.width * y].name

	def copy(self):
		newmap = GameMap(self.width, self.height, self.floor)
		for i in range(self.size):
			newmap.tiles[i] = self.tiles[i]
		newmap.exits = self.exits
		return newmap

	def getcostmap(self):
		result = [self.tiles[i].cost for i in range(self.size)]
		return result

	def getcost(self, x, y, wallszero=True, canswim=False):
		result = self.costmap[x + self.width * y]
		if (not wallszero):
			if (result == 0):
				# walls are finite but super big cost
				result = self.size
		if (not canswim):
			# TODO: entities can drown if they can't swim but try to anyway??
			if (result == water.cost):
				result = self.size
		return result

	def settile(self, point, tile):
		self.tiles[point[1] * self.width + point[0]] = tile.copy()

	def getgroundtiles(self):
		result = self.gettilesbytype('ground')
		return result

	def gettilesbytype(self, tilename):
		result = []
		for i in range(self.width):
			for j in range(self.height):
				point = tuple([i, j])
				if (self.tilename(*point) == tilename):
					result.append(point)
		# order: top to bottom -> left to right
		return result

	def generate(self, biomename, top=False, bottom=False, left=False, right=False):
		self.biomename = biomename
		self.tiles = self.cellularautomata().tiles
		self.costmap = self.getcostmap()
		self.setexits(top=top, bottom=bottom, left=left, right=right)
		self.costmap = self.getcostmap()

	def inbounds(self, x, y, buffer=0):
		return (x < self.width - buffer and
				x >= buffer and
				y < self.height - buffer and
				y >= buffer)

	def adjacenttile(self, point, tiletype, buffer=0):
		result = []
		x = point[0]
		y = point[1]

		if (self.inbounds(x-1, y, buffer) and
			self.tilename(x-1, y) == tiletype.name):
			result.append(tuple([x-1, y]))
		if (self.inbounds(x+1, y, buffer) and
			self.tilename(x+1, y) == tiletype.name):
			result.append(tuple([x+1, y]))
			
		if (self.inbounds(x, y-1, buffer) and
			self.tilename(x, y-1) == tiletype.name):
			result.append(tuple([x, y-1]))
		if (self.inbounds(x, y+1, buffer) and
			self.tilename(x, y+1) == tiletype.name):
			result.append(tuple([x, y+1]))
			
		if (self.inbounds(x-1, y-1, buffer) and
			self.tilename(x-1, y-1) == tiletype.name):
			result.append(tuple([x-1, y-1]))
		if (self.inbounds(x-1, y+1, buffer) and
			self.tilename(x-1, y+1) == tiletype.name):
			result.append(tuple([x-1, y+1]))
		if (self.inbounds(x+1, y-1, buffer) and
			self.tilename(x+1, y-1) == tiletype.name):
			result.append(tuple([x+1, y-1]))
		if (self.inbounds(x+1, y+1, buffer) and
			self.tilename(x+1, y+1) == tiletype.name):
			result.append(tuple([x+1, y+1]))

		return len(result)

	def check_can_reach_exit(self, pos):
		for e in self.exits.values():
                        path = False
                        if (not e is None):
                                path = astar(
                                        pos, e, self, travonly=True, buffer=0)
                        if path:
                                return True
		return False

	def setexits(self, top=False, left=False, right=False, bottom=False):
		newexits = []

		if top:
			xpos = random.choice(range(self.width))
			mapexit = (xpos, 0)
			self.exits['north'] = mapexit
			newexits.append(mapexit)	  
		if left:
			ypos = random.choice(range(self.height))
			mapexit = (0, ypos)
			self.exits['west'] = mapexit
			newexits.append(mapexit)
		if right:
			ypos = random.choice(range(self.height))
			mapexit = (self.width-1, ypos)
			self.exits['east'] = mapexit
			newexits.append(mapexit)
		if bottom:
			xpos = random.choice(range(self.width))
			mapexit = (xpos, self.height-1)
			self.exits['south'] = mapexit
			newexits.append(mapexit)

		# find path (through walls!) from each exit to another exit, 
		# make each tile along the path ground if it's a wall
		#assert(len(newexits) >= 2) 
		roomcenter = (int(self.width / 2), int(self.height / 2))
		for e in newexits:
			path = astar(
				e, roomcenter, self, travonly=False, costs=True, buffer=0)
			for pos in path:
				# only change walls (assumes player can swim)
				if (self.tilename(pos[0], pos[1]) == 'wall'):
					self.settile(pos, ground)
				# change water too (if player can't swim)
				if (self.tilename(pos[0], pos[1]) == 'water'):
					self.settile(pos, tree)

	def cellularautomata(self):
		newmap = GameMap(self.width, self.height, self.floor)

		scalemod = self.size / 8000 

		biome = biomes.get(self.biomename)

		percentwalls = biome.params['percentwalls']
		wallscalemod = biome.params['wallscalemod']
		percentwalls += wallscalemod * sqrt(scalemod)
		wallsize = biome.params['wallsize']
		
		percentwater = biome.params['percentwater']
		lakesize = biome.params['lakesize']
		
		percenttrees = biome.params['percenttrees']
		forestsize = biome.params['forestsize']

		gens = biome.params['gens']

		# walls
		for i in range(1, self.width-1):
			for j in range(1, self.height-1):
				newmap.settile(tuple([i, j]), ground)
				if ((j == self.height / 2 and
					 random.random() < percentwalls * 1.5) or
					random.random() < percentwalls):
					newmap.settile(tuple([i, j]), wall)

		for g in range(gens):
			oldmap = newmap.copy()
			for i in range(1, self.width-1):
				for j in range(1, self.height-1):
					point = tuple([i, j])
					adjwalls = oldmap.adjacenttile(point, wall)
					if (adjwalls >= 4 and
						random.random() < wallsize):
						newmap.settile(point, wall)
					else:
						newmap.settile(point, ground)

		# water
		for i in range(1, self.width-1):
			for j in range(1, self.height-1):
				if (random.random() < percentwater and
					newmap.tilename(i, j) == wall.name):
					newmap.settile(tuple([i, j]), water)

		for g in range(gens):
			oldmap = newmap.copy()
			for i in range(1, self.width-1):
				for j in range(1, self.height-1):
					point = tuple([i, j])
					adjwater = oldmap.adjacenttile(point, water)
					if (adjwater > 0 and
						random.random() < lakesize and
						not oldmap.tilename(i, j) == ground.name):
						newmap.settile(point, water)

		# trees
		for i in range(1, self.width-1):
			for j in range(1, self.height-1):
				if (random.random() < percenttrees and
					newmap.tilename(i, j) == ground.name):
					newmap.settile(tuple([i, j]), tree)

		for g in range(gens):
			oldmap = newmap.copy()
			for i in range(1, self.width-1):
				for j in range(1, self.height-1):
					point = tuple([i, j])
					adjtree = oldmap.adjacenttile(point, tree) + \
						oldmap.adjacenttile(point, water)
					if (adjtree > 0 and
						random.random() < forestsize and
						oldmap.tilename(i, j) == ground.name):
						newmap.settile(point, tree)

		return newmap

class Player():
    def __init__(self):
            self.x = 0
            self.y = 0

def main():    
    gamemap = None
    biomename = 'MEDROOM_MEDFOREST_SMLWATER'
    width, height, floor = (45, 40, 0)
    boolchoice = [True, False]
    player = Player()
    entities = []
    while(1):
        input()
        gamemap = GameMap(width, height, floor)
        exits = [random.choice(boolchoice),
                 random.choice(boolchoice),
                 random.choice(boolchoice),
                 random.choice(boolchoice)]
        if not True in exits:
                exits[0] = True
        gamemap.generate(biomename, exits[0], exits[1], exits[2], exits[3])
        print(list(gamemap.exits.values()))

        # print map
        for row in range(gamemap.height):
                row_tiles = gamemap.tiles[row*gamemap.width:(row+1)*gamemap.width]
                row_chars = [printtile[tile.name] for tile in row_tiles]
                for e in gamemap.exits.values():
                        if (not e is None and row == e[1]):
                                row_chars[e[0]] = '>'
                print(row, '\t', ''.join(row_chars))

if __name__=='__main__':
    main()




    
