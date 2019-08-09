from pathfinding import astar

biomes = [
	'tropical rainforest',
	'tropical savannah',
	'hot desert',	
	'hot steppe',	
	'humid continental',	
	'subarctic continental',	
	'mediterranean',	
	'humid subtropical',	
	'oceanic',	
	'coastal temp rainforest',
	'cold desert',	
	'cold steppe',	
	'tundra',	
	'ice cap',
	'volcano',
	'polar',
	'mountain'
]

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
	def __init__(self, pindex, worldtile, adjtiles, noisegrids, regionside=32):
		self.width = self.height = regionside

		# use to query noisegrids
		self.pindex = pindex
		self.noisegrids = noisegrids

		self.refreshtimes = 0
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
		self.forestdensity = 0
		self.numrivers = 0

		self.generateregion(adjtiles)

	def regiontile(self, x, y):
		result = self.tiles[x + self.width * y]
		return result

	def generateregion(self, adjtiles):
		if (self.biome in ['water', 'ice cap']):
			# maybe small islands?
			# icy shit on ice caps (but then how to handle poles?)
			# otherwise, all water
			for tile in self.tiles:
				tile.allwater = True
			return
		else:
			# first, do coasts and general elevation
			if (self.biome == 'volcano'):
				# special case for volcanos
				# tile.islava = True
				pass
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
					(MAX_MOUNTS-MIN_MOUNTS) * self.noisegrids[0].tiles[0])
				peaks = self.noisegrids[0].extremes(
					mindist=2, buffer=5, num=nummounts)
				print(peaks)
			else:
				pass