from random import random, choice, choices, randint, shuffle

# elevation/terrain
NUMFAULTS = 34
SMALLRADIUS = 1
BIGRADIUS = 14
FAULT_WIDTH = 2
ELEVATION_GENS = 6
ELEVATION_BUILD = 1.01
ELEVATION_SPREAD = 0.22
ELEVATION_EROSION = 0.003

# biome stuff
MIN_MOUNTS = 12
NUM_POLARS = 4
COASTAL_DIST = 2
STEPPE_FREQ = 0.9
WIND_HADLEY_BLOWOVER = 10

class WorldTile():
	def __init__(self, x, y):
		self.biome = 'water'
		self.elevation = 0.0
		self.position = (x, y)
		self.dist2coast = -1

class WorldMap():

	def __init__(self, mapwidth=64, mapheight=40):
		self.map_width = mapwidth
		self.map_height = mapheight

		self.tiles = []
		for y in range(self.map_height):
			for x in range(self.map_width):
				self.tiles.append(WorldTile(x, y))

		# latitude info
		self.interval = (int)(self.map_height/6) #30 degrees
		self.npolarcell = self.interval
		self.nmidcell = self.interval*2
		self.equator = self.interval*3
		self.smidcell = self.map_height-self.interval*2
		self.spolarcell = self.map_height-self.interval

		self.tilesperdegree = (float)(self.map_height/180)

		self.generateworld()

	def worldtile(self, x, y):
		result = self.tiles[x + self.map_width * y]
		return result

	def gettilesbybiome(self, *biomes):
		result = []
		for y in range(self.map_height):
			for x in range(self.map_width):
				if self.worldtile(x, y).biome in biomes:
					result.append((x, y))
		return result

	def adjacenttiles(self, x, y, diag=False, biomes=None):
		result = []
		xplus = x+1
		if (xplus >= self.map_width):
			xplus = 0
		xminus = x-1
		if (xminus < 0):
			xminus = self.map_width-1

		yplus = y+1
		yminus = y-1
		if (y == 0):
			yminus = None
		if (y == self.map_height-1):
			yplus = None

		result.append((xplus, y))
		result.append((xminus, y))
		if (not yplus is None):
			result.append((x, yplus))
		if (not yminus is None):
			result.append((x, yminus))

		if (diag):
			if (not yplus is None):
				result.append((xplus, yplus))
				result.append((xminus, yplus))
			if (not yminus is None):
				result.append((xplus, yminus))
				result.append((xminus, yminus))

		if (not biomes is None):
			result = [tile for tile in result \
				if self.worldtile(tile[0], tile[1]).biome in biomes]

		return result

	def moremountains(self, faultlines):
		for y in list(range(self.map_height))[self.npolarcell:self.spolarcell+1]:
			for x in list(range(self.map_width))[3:-3]:
				for i in range(len(faultlines)):
					if (i%2==1):
						fault = faultlines[i]
						if (abs((x-fault[0])**2 + (y-fault[1])**2 - \
							fault[2]**2) < 1):
							self.worldtile(x, y).elevation += 10.0

	def generateelevation(self):
		elevationtiles = [0.0] * self.map_width * self.map_height
		newmap = elevationtiles[:]

		# generate faults
		faultlines = []
		for i in range(NUMFAULTS):
			x = choice(range(self.map_width))
			y = choice(range(self.map_height))
			radius = 0
			if (i%2==0):
				radius = SMALLRADIUS
			else:
				radius = BIGRADIUS
			faultlines.append([x, y, radius])
			faultlines.append([x+self.map_width, y, radius])
			faultlines.append([x-self.map_width, y, radius])

		for gen in range(ELEVATION_GENS):
			# add from faults
			for y in list(range(self.map_height))[self.npolarcell:self.spolarcell+1]:
				for x in list(range(self.map_width))[3:-3]:
					for fault in faultlines:
						if (abs((x-fault[0])**2 + (y-fault[1])**2 - \
							fault[2]**2) <= FAULT_WIDTH**2):
							elevationtiles[x + self.map_width * y] += ELEVATION_BUILD

			# spread the love
			newmap = elevationtiles[:]
			for y in range(self.map_height):
				for x in range(self.map_width):
					if (newmap[x + self.map_width * y] > 0):
						adjtiles = self.adjacenttiles(x, y)
						for adjtile in adjtiles:
							newmap[adjtile[0] + self.map_width * adjtile[1]] += \
								newmap[x + self.map_width * y] * ELEVATION_SPREAD
						newmap[x + self.map_width * y] *= ELEVATION_EROSION
			elevationtiles = newmap[:]

		# copy elevations to appropriate tiles
		for y in range(self.map_height):
			for x in range(self.map_width):
				self.worldtile(x, y).elevation = \
					elevationtiles[x + self.map_width * y]

		self.moremountains(faultlines)

		# map ground, mountain and water biomes
		for y in range(self.map_height):
			for x in range(self.map_width):
				self.setterrain(x, y)

		# map polar mountain biomes
		if (self.raisepeaks() == False):
			return False
		return True

	def setterrain(self, x, y):
		tile = self.worldtile(x, y)
		tileelev = tile.elevation
		if (tileelev >= 1.0 and tileelev < 3.5):
			tile.biome = 'ground'
		elif (tileelev >= 3.5):
			tile.biome = 'mountain'

	def raisepeaks(self):
		mountains = self.gettilesbybiome('mountain')
		if (len(mountains) < MIN_MOUNTS):
			return False

		numpolars = 0

		# raise some mountain peaks
		# assumes MIN_MOUNTS > NUM_POLARS
		shuffle(mountains)
		for mt in mountains:
			if len(self.adjacenttiles(mt[0], mt[1], 
					diag=True, biomes=['mountain'])) >= 6:
				self.worldtile(mt[0], mt[1]).biome = 'polar'	
				numpolars += 1

				if (numpolars >= NUM_POLARS):
					return True

		if (numpolars < NUM_POLARS):
			return False

	def getwind(self, degrees):
		wind = (0, 0)
		if degrees < 30:
			# polar cell, north
			wind = (-1, 1)
		elif degrees < 60:
			# ferrel cell, north
			wind = (1, -1)
		elif degrees < 90:
			# hadley cell, north
			wind = (-1, 1)
		elif degrees < 120:
			# hadley cell, south
			wind = (-1, -1)
		elif degrees < 150:
			# ferrel cell, south
			wind = (1, 1)
		else:
			# polar cell, south
			wind = (-1, -1)
		return wind

	def getcoastinfo(self, x, y):
		dist = 1
		waterfound = []

		while (dist<(self.map_width/2+1)):
			xplus = (x+dist)%self.map_width
			yplus = min((y+dist), self.map_height-1)
			if (self.worldtile(xplus, y).biome == 'water'):
				waterfound.append(((1, 0), dist))
			if (self.worldtile(x, yplus).biome == 'water'):
				waterfound.append(((0, 1), dist))

			xminus = (x+self.map_width-dist)%self.map_width
			yminus = max((y-dist), 0)
			if (self.worldtile(xminus, y).biome == 'water'):
				waterfound.append(((-1, 0), dist))
			if (self.worldtile(x, yminus).biome == 'water'):
				waterfound.append(((0, -1), dist))

			if (self.worldtile(xplus, yplus).biome == 'water'):
				waterfound.append(((1, 1), dist+1))
			if (self.worldtile(xplus, yminus).biome == 'water'):
				waterfound.append(((1, -1), dist+1))
			if (self.worldtile(xminus, yplus).biome == 'water'):
				waterfound.append(((-1, 1), dist+1))
			if (self.worldtile(xminus, yminus).biome == 'water'):
				waterfound.append(((-1, -1), dist+1))
			dist += 1

		return waterfound

	def getrainshadow(self, x, y, degrees, wind, mountains):
		raindepth = 1

		northbounds = degrees - degrees%30
		southbounds = northbounds + 30
		wx, wy = wind

		#print(northbounds, southbounds, wx, wy, x, y)

		# follow wind vector backwards to check for mountain
		# stop when the wind cell ends, or when a mountain is found
		px = x-wx
		py = y-wy
		degrees = (int)((float)(py)/self.tilesperdegree)
		while (degrees >= northbounds and degrees < southbounds):
			if ((px, py) in mountains):
				raindepth -= 2 # shadow tiles per mountain width
			if (raindepth < 1):
				return True
			else:
				px = px-wx
				py = py-wy
				degrees = (int)((float)(py)/self.tilesperdegree)
				raindepth += 1

		return False

	def getcurrenttemp(self, degrees, coastinfo):
		result = None # None if inland, not coastal
		for direction, dist in coastinfo:
			if dist <= COASTAL_DIST:
				if degrees < 10:
					# north polar gyre
					if direction[0] > 0:
						result = 'cold'
					elif direction[0] < 0:
						result = 'warm'
				elif degrees < 20:
					# north ferrel gyre
					if direction[0] > 0:
						result = 'warm'
					elif direction[0] < 0:
						result = 'cold'
				elif degrees < 50:
					# north midlat gyre
					if direction[0] > 0:
						result = 'cold'
					elif direction[0] < 0:
						result = 'warm'
				elif degrees < 90:
					# north hadley gyre
					if direction[0] > 0:
						result = 'warm'
					elif direction[0] < 0:
						result = 'cold'
				elif degrees < 130:
					# south hadley gyre
					if direction[0] > 0:
						result = 'warm'
					elif direction[0] < 0:
						result = 'cold'
				elif degrees < 160:
					# south midlat gyre
					if direction[0] > 0:
						result = 'cold'
					elif direction[0] < 0:
						result = 'warm'
				elif degrees < 170:
					# south ferrel gyre
					if direction[0] > 0:
						result = 'warm'
					elif direction[0] < 0:
						result = 'cold'
				else:
					# south polar gyre
					if direction[0] > 0:
						result = 'cold'
					elif direction[0] < 0:
						result = 'warm'
				return result

	def getonshorewind(self, y, degrees, wind, coastinfo, rainshadow):
		if rainshadow:
			return False

		northbounds = degrees - degrees%30
		southbounds = northbounds + 30

		# hadley cell winds blow onshore into the opposite hadley cell a bit
		if (northbounds == 90):
			northbounds -= WIND_HADLEY_BLOWOVER
		if (southbounds == 90):
			southbounds += WIND_HADLEY_BLOWOVER

		# for each coast
		for direction, dist in coastinfo:
			# determine coast latitude
			coastdegrees = (int)((float)(y + direction[1]*dist)/self.tilesperdegree)
			# if in the same wind cell
			if (coastdegrees >= northbounds and coastdegrees <= southbounds):
				# if the coast is in the direciton the wind blows from
				if (direction == wind):
					return True

		return False

	def dist2coast(self, coastinfo):
		if (coastinfo is None or len(coastinfo) <= 0):
			return None

		mindist = coastinfo[0][1]
		#mindirection = coastinfo[0][0]

		for direction, dist in coastinfo:
			if dist < mindist:
				mindist = dist
				#mindirection = direction

		return mindist

	def setbiome(self, x, y, 
		degrees, dist2coast,
		coastinfo, currenttemp, 
		rainshadow, onshorewind):

		tile = self.worldtile(x, y)
		assert(tile.biome == 'ground')

		# HADLEY CELL
		if (degrees >= 80 and degrees <= 100 and
			onshorewind):
			tile.biome = 'tropical rainforest'
		elif (degrees >= 70 and degrees <= 110 and 
			not rainshadow):
			tile.biome = 'tropical savannah'
		elif (degrees >= 60 and degrees <= 120 and 
			onshorewind and
			dist2coast <= COASTAL_DIST and
			currenttemp == 'warm'):
			tile.biome = 'tropical savannah'
		elif ((degrees <= 80 and degrees >= 60 or
			degrees <= 120 and degrees >= 100) and
			currenttemp != 'warm' and
			not onshorewind):
			tile.biome = 'hot desert'
		elif (degrees <= 120 and degrees >= 60):
			tile.biome = 'hot steppe'

		# FERREL CELL and POLAR CELL
		if ((degrees <= 150 and degrees >= 120 or
			degrees <= 60 and degrees >= 30)):
			tile.biome = 'humid continental'
		# carve away at humid continental
		if ((degrees <= 160 and degrees >= 135 or
			degrees <= 45 and degrees >= 20)):
			tile.biome = 'subarctic continental'
		# carve into more unique biomes
		if ((degrees <= 135 and degrees >= 120 or
			degrees <= 60 and degrees >= 45) and
			onshorewind and
			currenttemp == 'cold' and
			dist2coast < COASTAL_DIST):
			tile.biome = 'mediterranean'
		elif ((degrees <= 135 and degrees >= 120 or
			degrees <= 60 and degrees >= 45) and
			onshorewind and
			currenttemp == 'warm' and
			dist2coast <= COASTAL_DIST):
			tile.biome = 'humid subtropical'
		elif ((degrees <= 150 and degrees >= 130 or
			degrees <= 50 and degrees >= 30) and
			currenttemp == 'warm'):
			tile.biome = 'oceanic'
		if ((degrees <= 135 and degrees >= 120 or
			degrees <= 60 and degrees >= 45) and
			onshorewind and
			currenttemp == 'warm' and
			dist2coast <= 1):
			if (choices([True, False], [0.5, 0.5])[0]):
				tile.biome = 'coastal temp rainforest'
		if ((degrees <= 160 and degrees >= 120 or
			degrees <= 60 and degrees >= 20) and
			not onshorewind and
			dist2coast > COASTAL_DIST*1.5):
			tile.biome = 'cold desert'
		# do cold step in setsteppes()
		if ((degrees <= 170 and degrees >= 150 or
			degrees <= 30 and degrees >= 10)):
			tile.biome = 'tundra'
		elif ((degrees >= 175 or degrees <= 15)):
			tile.biome = 'ice cap'

	def setsteppes(self):
		newmap = {}

		for y in range(self.map_height):
			for x in range(self.map_width):
				adjtiles = self.adjacenttiles(x, y, True)
				adjbiomes = [self.worldtile(*tile).biome for tile in adjtiles]
				if ('cold desert' in adjbiomes and
					self.worldtile(x, y).biome in [
						'tropical savannah',
						'humid subtropical',
						'humid continental',
						'subarctic continental']):
					FREQ = STEPPE_FREQ
					if (choices([True, False], [STEPPE_FREQ, 1.0-STEPPE_FREQ])[0]):
						newmap[(x, y)] = 'cold steppe'
		for y in range(self.map_height):
			for x in range(self.map_width):
				adjtiles = self.adjacenttiles(x, y, True)
				adjbiomes = [self.worldtile(*tile).biome for tile in adjtiles]
				if ('hot desert' in adjbiomes and
					self.worldtile(x, y) in [
						'tropical savannah',
						'humid subtropical',
						'humid continental',
						'tropical rainforest']):
					FREQ = STEPPE_FREQ
					if (choices([True, False], [STEPPE_FREQ, 1.0-STEPPE_FREQ])[0]):
						newmap[(x, y)] = 'hot steppe'

		# copy new biomes over
		for x, y in newmap:
			self.worldtile(x, y).biome = newmap[(x, y)]

	def generatebiomes(self):
		mountains = self.gettilesbybiome('mountain', 'polar')

		for y in range(self.map_height):
			degrees = (int)((float)(y)/self.tilesperdegree)
			wind = self.getwind(degrees)
			ice_prob = 0.0
			if (degrees >= 165 or degrees < 10):
				ice_prob = 1.0-float(min(175-degrees, degrees))/10.0
			for x in range(self.map_width):
				tile = self.worldtile(x, y)

				coastinfo = None
				nearestcoast = None
				if (tile.biome != 'water'):
					coastinfo = self.getcoastinfo(x, y)
					nearestcoast = self.dist2coast(coastinfo)
					tile.dist2coast = nearestcoast

				if (tile.biome == 'ground'):
					adjtiles = self.adjacenttiles(x, y, True)
					rainshadow = self.getrainshadow(
						x, y, degrees, wind, mountains)
					onshorewind = self.getonshorewind(
						y, degrees, wind, coastinfo, rainshadow)
					currenttemp = self.getcurrenttemp(degrees, coastinfo)
					self.setbiome(x, y, 
						degrees, nearestcoast,
						coastinfo, currenttemp,
						rainshadow, onshorewind)
				if (tile.biome == 'water'):
					if (choices([True, False], [ice_prob, 1.0-ice_prob])[0]):
						tile.biome = 'ice cap'
				if (tile.biome == 'mountain'):
					if (len(
						self.adjacenttiles(
							x, y, True, ['water', 'ice cap'])) >= 8):

						tile.biome = 'volcano'

		# transition from deserts into steppes
		self.setsteppes()

		return True

	def generateworld(self):
		coolworld = False

		while (not coolworld):
			coolworld = self.generateelevation()
			self.generatebiomes()