from pathfinding import astar, vectorsbyclosestangle
from dataloader import getdata
from random import choices
from numpy import dot
from math import sin, cos

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
MAX_MOUNTS = 5
MIN_MOUNTS = 3
TILES2COAST_CONN = 5
TILES2ELEV_CONN = 8
MAX_MOUNTLAYERS = 7
MIN_MOUNTLAYERS = 3
MOUNTLAYER_WIDTH = 3
VOLCANO_LAYERS = 8
RIVERSPAWNRADIUS = 12
RIVERFORESTMOD = 1.5
MOUNTSLOPEFORESTMOD = 2.0

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

	def newriverinputs(self, waterinputdirs):
		cx, cy = (self.width//2, self.height//2)
		avgx, avgy = (0, 0)
		for winput in waterinputdirs:
			avgx += avgx + winput[0]
			avgy += avgy + winput[1]
		riverinputs = []
		angle = -0.5 # radians
		while (len(riverinputs) < self.numrivers and angle < 7.0):
			x, y = (
				int(RIVERSPAWNRADIUS * cos(angle)),
				int(RIVERSPAWNRADIUS * sin(angle)))
			if ((dot((x, y), (avgx, avgy)) > 0  or 
				(avgx, avgy) == (0, 0)) and
				self.inbounds(x+cx, y+cy)):
				riverinputs.append((x+cx, y+cy))
			angle += self.tnoisegrids[1].tiles[0] # 0.0 <= x < 1.0
		return riverinputs

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
						if (terrainnoise.get(*newpos) > 0.25):
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
							self.tnoisegrids[0].size // 2])
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
								elif (xysq == 0):
									self.regiontile(x, y).elevationdir = None

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
									elif (xysq == 0):
										self.regiontile(x, y).elevationdir = None

			# third, do rivers
			if (not self.biome in ['ice cap', 'volcano', 'polar', 'mountain']):
				upslopedirections = [direction \
					for direction in adjtiles \
					if (adjtiles[direction].dist2coast > self.dist2coast) and
					0 in direction]
				# 1) find center
				cx, cy = (self.width//2, self.height//2) # (16, 16)
				# 2) path from center to one output, and from inputs to center
				riveroutput = None
				if (len(downslopedirections) > 0):
					riveroutput = (
						min(cx+downslopedirections[0][0]*self.width//2, 
							self.width-1),
						min(cy+downslopedirections[0][1]*self.height//2, 
							self.height-1))

				riverinputs = []
				riverinputs.extend(self.newriverinputs(upslopedirections))
				for updir in upslopedirections:
					x, y = (
						min(cx+updir[0]*self.width//2, self.width-1),
						min(cy+updir[1]*self.height//2, self.height-1))
					riverinputs.append((x, y))

				self.setneighbors(True)
				riverpathtoout = None
				if (not riveroutput is None):
					riverpathtoout = astar(
						(cx, cy), riveroutput, self, terrainnoise)
				riverpathsfromin = []
				for riverin in riverinputs:
					path = astar(riverin, (cx, cy), self, terrainnoise)
					riverpathsfromin.append(path)
				
				# 3) draw paths, stop when hitting another river
				if (not riverpathtoout is None):
					prevtile = riverpathtoout[0]
					for i in range(len(riverpathtoout)):
						x, y = riverpathtoout[i]
						riverdir = None
						if (i-1 >= 0):
							prevx, prevy = riverpathtoout[i-1]
							riverdir = (x-prevx, y-prevy)
						else:
							x2, y2 = riverpathtoout[i+1]
							riverdir = (x2-x, y2-y)
						regtile = self.regiontile(x, y)
						if (regtile.riverdir is None and
							not regtile.allwater):
							regtile.riverdir = riverdir
						else:
							break

				for path in riverpathsfromin:
					for i in range(len(path)):
						x, y = path[i]
						riverdir = None
						if (i+1 < len(path)):
							x2, y2 = path[i+1]
							riverdir = (x2-x, y2-y)
						regtile = self.regiontile(x, y)
						if (regtile.riverdir is None and
							not regtile.allwater):
							regtile.riverdir = riverdir
						else:
							break

				# 4) if hit a river going opposite directions, form a lake
				valleys = terrainnoise.extremes(
					mindist=5, minmax='min', buffer=6, num=self.numlakes)
				if (riverpathtoout is None):
					self.regiontile(cx, cy).allwater = True
				for v in valleys:
					self.regiontile(*v).allwater = True

			# last, do forests
			for y in range(self.height):
				for x in range(self.width):
					p = 1.0 - terrainnoise.get(x, y)
					adjregtiles = self.adjacenttiles(x, y, True)
					adjregtiles.append((x, y))
					for tile in adjregtiles:
						if (not self.regiontile(*tile).riverdir is None):
							p /= RIVERFORESTMOD
					if (not self.regiontile(x, y).riverdir is None):
						p /= RIVERFORESTMOD
					if (self.biome == 'mountain' and
						not self.regiontile(x, y).elevationdir is None):
						p *= MOUNTSLOPEFORESTMOD
					if (p < self.forestdensity):
						self.regiontile(x, y).forest = True

			##### END OF TERRAIN, BEGIN POIs AND METADATA ###########

			# first, do towns (no towns on ice caps for now)
			# (clear out forests)

			# second, do roads

			# third, do POIs

			# last, do dungeons