from pathfinding import astar
from dataloader import getdata
from random import choices

biomedata = getdata('biome')

pois = [
	'cave', # place on elevation changes, rifts and coasts
	'temple', # place on roads
	'house',
	'temple',
	'tavern',
	'town'
]

# elevation/terrain
MAX_MOUNTS = 12
MIN_MOUNTS = 8
TILES2COAST_CONN = 6
MAXELEVATIONLINETILES = 6

class RegionTile():
	def __init__(self, x, y):
		self.allwater = False # use to just cover with water (ocean, lake)
		self.islava = False # use in the center of volcano regions
		self.coastdirs = []	# use to make coastlines for oceans and lakes
		self.poi = '' # determine to place a poi (only one allowed)
		self.forest = False

		# only cardinal and diagonals
		self.riverdir = None 
		self.elevationdir = None
		self.roaddir = None		

class RegionMap():
	def __init__(self, x, y, world, noisegrids, regionside=32):
		self.width = self.height = regionside

		worldtile = world.worldtile(x, y)
		adjtiles = world.adjacenttiles(x, y)

		# use to query noisegrids
		self.pindex = worldtile.position[0] + \
			world.map_width * worldtile.position[1]

		# same noise everyone else has
		self.noisegrids = noisegrids

		# translated noise grids (personal noise)
		rand = self.noisegrids[0].tiles[self.pindex]
		self.tnoisegrids = [grid.translate(
			int(float(world.map_width)*rand), 
			int(float(world.map_height)*rand)) \
			for grid in self.noisegrids]

		self.biome = worldtile.biome

		self.tiles = []
		for y in range(self.height):
			for x in range(self.width):
				self.tiles.append(RegionTile(x, y))

		# meta info
		dungeonentrances = {} # (x, y) -> dungeonId
		dungeons = {} # dungeonId -> Dungeon()
		towns = {} # (x, y) -> Town()

		# terrain info
		self.coastdir = worldtile.dir2coast
		self.elevation = worldtile.dist2coast

		# load from biome data
		self.forestdensity = biomedata[self.biome]['forestdensity']
		self.numrivers = biomedata[self.biome]['numrivers']
		self.numlakes = biomedata[self.biome]['numlakes']
		self.weather = biomedata[self.biome]['weather']
		############ Add different weather for each season later ###########

		changesperday = biomedata[self.biome]['changesperday']
		self.refreshtimes = [i*24.0/changesperday \
			for i in range(changesperday)]

		self.generateregion(adjtiles)

	def getweather(self):
		options = []
		probs = []
		for key in self.weather:
			options.append(key)
			probs.append(self.weather[key])
		result = choices(options, probs)
		return result

	def regiontile(self, x, y):
		result = self.tiles[x + self.width * y]
		return result

	def genvolcanoregion(self):
		pass

	def generateregion(self, adjtiles):
		if (self.biome in ['water', 'ice cap']):
			# maybe small islands?
			# icy shit on ice caps (but then how to handle poles?)
			# otherwise, all water
			for tile in self.tiles:
				tile.allwater = True
			return
		else:
			terrainnoise = self.noisegrids[0].add(self.tnoisegrids[0])

			# first, do coasts and general elevation
			if (self.biome == 'volcano'):
				# special case for volcanos
				self.genvolcanoregion()
				return
			elif (self.elevation == 1):
				# coastal, adjacent
				pass
			elif (self.elevation == 1.4):
				# coastal, diagonal
				pass
			else:
				# non-coastal, do general elevation lines
				pass
			# second, do hills and mountains
			if (self.biome in ['mountain', 'polar']):
				nummounts = MIN_MOUNTS + int(
					(MAX_MOUNTS-MIN_MOUNTS) * self.noisegrids[0].tiles[self.pindex])
				peaks = self.noisegrids[0].extremes(
					mindist=2, buffer=5, num=nummounts)
				print(peaks)
			else:
				pass

			# third, do rivers
			if (self.biome != 'ice cap'):
				pass
			else:
				pass

			##### END OF TERRAIN, BEGIN POIs AND METADATA ###########

			# first, do towns (no towns on ice caps for now)

			# second, do roads

			# third, do POIs

			# last, do dungeons