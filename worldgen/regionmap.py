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

regiontiles = []
pointsofinterest = {}
dungeonsystems = {}

class RegionTile():
	def __init__(self, x, y):
		self.allwater = False # use to just cover with water (ocean, lake)
		self.coastdirs = []	# use to make coastlines for oceans and lakes
		self.poi = '' # determine to place a poi (only one allowed)
		self.riverdir = None
		self.roaddir = None
		self.elevationdir = None
		self.forest = False

class RegionMap():
	def __init__(self, pindex, worldtile, p1, p2, p3, regionside=32):
		self.width = self.height = regionside

		# use to query noisemaps
		self.pindex = pindex

		self.refreshtimes = 0
		self.biome = worldtile.biome

		self.tiles = []
		for y in range(self.height):
			for x in range(self.width):
				self.tiles.append(RegionTile(x, y))

		# terrain info
		self.coastdir = worldtile.dir2coast
		self.iscoast = (worldtile.dist2coast == 1)

		# load from biome data
		self.forestdensity = 0
		self.numrivers = 0

		self.generateregion()

	def regiontile(self, x, y):
		result = self.tiles[x + self.width * y]
		return result

	def generateregion(self):
		if (self.biome in ['water', 'ice cap']):
			# maybe small islands?
			# icy shit on ice caps (but then how to handle poles?)
			# otherwise, all water
			for tile in self.tiles:
				tile.allwater = True
		else:
			for tile in self.tiles:
				self.generatetile(tile)

	def generatetile(self, regiontile):
		pass
