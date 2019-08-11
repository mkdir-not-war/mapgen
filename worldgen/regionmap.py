from pathfinding import astar, vectorsbyclosestangle
from dataloader import getdata
from random import choices
from numpy import dot

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
MAX_MOUNTS = 5#12
MIN_MOUNTS = 3#8
TILES2COAST_CONN = 5
TILES2ELEV_CONN = 8
MAX_MOUNTLAYERS = 7
MIN_MOUNTLAYERS = 3
MOUNTLAYER_WIDTH = 3
VOLCANO_LAYERS = 8

class RegionTile():
	def __init__(self, x, y):
		self.debugflag = False

		self.allwater = False # use to just cover with water (ocean, lake)
		self.islava = False # use in the center of volcano regions
		self.coastdirs = []	# use to make coastlines for oceans and lakes
		self.poi = '' # determine to place a poi (only one allowed)
		self.forest = False

		# cardinal and diagonals (only cardinal at zoomed in level)
		self.elevationdir = None
		self.roaddir = None	

		# only cardinal (used to determine direction of flow)
		self.riverdir = None 

class RegionMap():
	def __init__(self, x, y, world, noisegrids, regionside):
		self.width = self.height = regionside
		self.size = regionside**2

		self.worldpos = (x, y)

		worldtile = world.worldtile(x, y)

		adjpos = world.adjacenttiles(x, y, True)
		adjtiles = {}
		for pos in adjpos:
			relpos = (pos[0]-x, pos[1]-y)
			adjtiles[relpos] = world.worldtile(pos[0], pos[1])

		# use to query noisegrids
		self.pindex = worldtile.position[0] + \
			world.map_width * worldtile.position[1]

		# same noise everyone else has
		# (deep copy, so doesn't use a ton of memory)
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
		self.dist2coast = worldtile.dist2coast

		# load from biome data
		self.forestdensity = 0
		self.numrivers = 0
		self.numlakes = 0
		self.weather = []
		self.refreshtimes = []
		if (self.biome in biomedata):
			self.forestdensity = biomedata[self.biome]['forestdensity']
			self.numrivers = biomedata[self.biome]['numrivers']
			self.numlakes = biomedata[self.biome]['numlakes']
			self.weather = biomedata[self.biome]['weather']
			############ Add different weather for each season later ###########

			changesperday = biomedata[self.biome]['changesperday']
			self.refreshtimes = [i*24.0/changesperday \
				for i in range(changesperday)]
			self.numhills = 4#biomedata[self.biome]['numhills']

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

	def inbounds(self, x, y, buffer=0):
		result = (x-buffer >= 0 and
			x+buffer < self.width and
			y-buffer >= 0 and
			y+buffer < self.height)
		return result

	def setneighbors(self, diag):
		if (diag):
			self.neighbors = self.diagneighbors
		else:
			self.neighbors = self.cardneighbors

	def diagneighbors(self, pos):
		return self.adjacenttiles(pos[0], pos[1], True)

	def cardneighbors(self, pos):
		return self.adjacenttiles(pos[0], pos[1], False)

	def adjacenttiles(self, x, y, diag=False):
		result = []

		xplus = x+1
		xminus = x-1
		if (xminus < 0):
			xminus = None
		if (xplus >= self.width):
			xplus = None

		yplus = y+1
		yminus = y-1
		if (yminus < 0):
			yminus = None
		if (yplus >= self.height):
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

	def coaststartstop(self, waterdir, buffer):
		w = self.width-1
		h = self.height-1
		d = buffer

		if (waterdir == (1,0)):
			return (w-d, h), (w-d, 0)
		elif (waterdir == (0, -1)):
			return (0, d), (w, d)

		elif (waterdir == (0, 1)):
			return (0, h-d), (w, h-d)
		elif (waterdir == (-1, 0)):
			return (d, h), (d, 0)
		
		elif (waterdir == (1, 1)):
			return (w-d, h), (w, h-d)
		elif (waterdir == (-1, 1)):
			return (0, h-d), (d, h)
		elif (waterdir == (1, -1)):
			return (w, d), (w-d, 0)
		elif (waterdir == (-1, -1)):
			return (0, d), (d, 0)

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
			terrainnoise = terrainnoise.sizedown(2)

			# first, do coasts and general dist2coast
			'''
			if (self.biome == 'volcano'):
				# special case for volcanos
				self.genvolcanoregion()
				return
			'''

			if (self.dist2coast < 2):
				# coastal, adjacent
				waterdirections = [direction \
					for direction in adjtiles \
					if (adjtiles[direction].biome == 'water')]
				for waterdir in waterdirections:
					start, stop = self.coaststartstop(waterdir, TILES2COAST_CONN)
					if (not 0 in waterdir):
						self.setneighbors(False)
					else:
						self.setneighbors(True)
					path = astar(start, stop, self, terrainnoise)
					for pos in path:
						self.regiontile(*pos).allwater = True
						dist = 1
						newpos = (
							pos[0]+waterdir[0]*dist, 
							pos[1]+waterdir[1]*dist)
						while (self.inbounds(*newpos)):
							self.regiontile(*newpos).allwater = True
							dist += 1
							newpos = (
								pos[0]+waterdir[0]*dist, 
								pos[1]+waterdir[1]*dist)
			
			# do general elevation lines
			# only interested in cardinal direction adjacent tiles
			downslopedirections = [direction \
				for direction in adjtiles \
				if (adjtiles[direction].dist2coast < self.dist2coast) and
				0 in direction]
			self.setneighbors(True)
			for downslopedir in downslopedirections:
				start, stop = self.coaststartstop(downslopedir, TILES2ELEV_CONN)
				path = astar(start, stop, self, terrainnoise)
				for pos in path:
					if (self.regiontile(*pos).allwater):
						continue
					self.regiontile(*pos).elevationdir = downslopedir
					dist = 1
					newpos = (
						pos[0]+downslopedir[0]*dist, 
						pos[1]+downslopedir[1]*dist)
					while (self.inbounds(*newpos)):
						if (terrainnoise.get(*newpos) > 
							terrainnoise.amplitude / 4.0):
							self.regiontile(*newpos).elevationdir = None
						else:
							self.regiontile(*newpos).elevationdir = \
								downslopedir
						dist += 1
						newpos = (
							pos[0]+downslopedir[0]*dist, 
							pos[1]+downslopedir[1]*dist)

			# second, do hills and mountains
			if (self.biome in ['mountain', 'polar', 'volcano']):
				nummounts = MIN_MOUNTS + int(
					(MAX_MOUNTS-MIN_MOUNTS) * \
					terrainnoise.tiles[0])
				buffer = 6
				if (self.biome == 'volcano'):
					nummounts = 1
					buffer = 11
				peaks = terrainnoise.extremes(
					mindist=5, buffer=buffer, num=nummounts)

				mountlayers = []
				for i in range(nummounts):
					x, y = peaks[i]
					numlayers = MIN_MOUNTLAYERS + int(
						(MAX_MOUNTLAYERS-MIN_MOUNTLAYERS) * \
						self.tnoisegrids[0].tiles[i * \
							self.tnoisegrids[0].size // 2] // \
						self.tnoisegrids[0].amplitude)
					if (self.biome == 'volcano'):
						numlayers = VOLCANO_LAYERS
					radius = MOUNTLAYER_WIDTH+0.2
					for j in range(numlayers):
						mountlayers.append([x, y, radius])
						radius += 1

				if (self.biome == 'volcano'):
					self.regiontile(
						mountlayers[0][0], mountlayers[0][1]).islava = True
				for y in range(self.height):
					for x in range(self.width):
						for layer in mountlayers:
							xysq = (x-layer[0])**2 + (y-layer[1])**2
							if (xysq <= layer[2]**2):
								if (self.regiontile(x, y).allwater):
									self.regiontile(x, y).allwater = False
								if (abs(xysq - layer[2]**2) <= \
									MOUNTLAYER_WIDTH**2):
									diff = (x-layer[0], y-layer[1])
									vec = vectorsbyclosestangle(
										diff,
										[(1,0), (-1,0),
										(0,1), (0,-1),
										(1,1), (-1,1),
										(1,-1), (-1,-1)])
									if (self.regiontile(x, y).elevationdir is None or
										dot(self.regiontile(x, y).elevationdir, 
											vec) > 0):

										self.regiontile(x, y).elevationdir = vec

			else:
				# hills only have 1 layer
				numhills = int(self.numhills * terrainnoise.tiles[0])
				if (numhills > 0):
					peaks = terrainnoise.extremes(
						mindist=5, buffer=6, num=numhills)

					hilllayers = []
					for i in range(numhills):
						x, y = peaks[i]
						radius = 1
						hilllayers.append([x, y, radius])

					for y in range(self.height):
						for x in range(self.width):
							for layer in hilllayers:
								xysq = (x-layer[0])**2 + (y-layer[1])**2
								if (xysq <= layer[2]**2):
									if (self.regiontile(x, y).allwater):
										self.regiontile(x, y).allwater = False
									if (abs(xysq - layer[2]**2) <= 2 and
										xysq != 0):

										diff = (x-layer[0], y-layer[1])
										vec = vectorsbyclosestangle(
											diff,
											[(1,0), (-1,0),
											(0,1), (0,-1),
											(1,1), (-1,1),
											(1,-1), (-1,-1)])
										self.regiontile(x, y).elevationdir = vec

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