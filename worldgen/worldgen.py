import sys
import tcod as libtcod
import tcod.event
from random import random, choice, choices, randint, seed, shuffle
from numpy import multiply

colors = {
	'black': libtcod.black,
	'ground': libtcod.Color(204, 120, 96),
	'mountain': libtcod.Color(179, 51, 16),
	'water': libtcod.desaturated_blue * libtcod.lighter_grey,
	'polar': libtcod.lightest_blue * libtcod.white,

	'tropical rainforest': libtcod.darker_green,	
	'tropical savannah': libtcod.gold * libtcod.lighter_chartreuse,	
	'hot desert': libtcod.gold,	
	'hot steppe': libtcod.red * libtcod.gold,	

	'humid continental': libtcod.Color(143, 181, 100) * libtcod.lightest_grey,	
	'subarctic continental': libtcod.Color(143, 181, 100) * libtcod.grey,	
	'mediterranean': libtcod.purple,	
	'humid subtropical': libtcod.purple * libtcod.lighter_blue,	
	'oceanic': libtcod.dark_orange,	
	'coastal temp rainforest': libtcod.darker_purple,
	'cold desert': libtcod.gold * libtcod.lightest_grey,	
	'cold steppe': libtcod.light_red * libtcod.lighter_blue,	

	'tundra': libtcod.lightest_blue * libtcod.lighter_grey,	
	'ice cap': libtcod.lightest_blue * libtcod.white
}

screen_width = 80 # /4 = 20
screen_height = 50 # /4 ~= 12

# Map panel parameters
map_width = 64
map_height = 40

draw_offset_x = (int)((screen_width - map_width) / 2)
draw_offset_y = (int)((screen_height - map_height) / 2)

elevationtiles = []
worldtiles = []

# latitude info
interval = (int)(map_height/6) #30 degrees
npolarcell = interval
nmidcell = interval*2
equator = interval*3
smidcell = map_height-interval*2
spolarcell = map_height-interval

tilesperdegree = (float)(map_height/180)

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
STEPPE_FREQ = 0.8
WIND_HADLEY_BLOWOVER = 10

def adjacenttiles(x, y, diag=False, tiletypes=None):
	result = []
	xplus = x+1
	if (xplus >= map_width):
		xplus = 0
	xminus = x-1
	if (xminus < 0):
		xminus = map_width-1

	yplus = y+1
	yminus = y-1
	if (y == 0):
		yminus = None
	if (y == map_height-1):
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

	if (not tiletypes is None):
		result = [tile for tile in result \
			if worldtile(tile[0], tile[1]) in tiletypes]

	return result

def generateelevation():
	global elevationtiles
	elevationtiles = [0.0] * map_width * map_height

	# generate faults
	faultlines = []
	for i in range(NUMFAULTS):
		x = choice(range(map_width))
		y = choice(range(map_height))
		radius = 0
		if (i%2==0):
			radius = SMALLRADIUS
		else:
			radius = BIGRADIUS
		faultlines.append([x, y, radius])
		faultlines.append([x+map_width, y, radius])
		faultlines.append([x-map_width, y, radius])

	for gen in range(ELEVATION_GENS):
		# add from faults
		for y in list(range(map_height))[npolarcell:spolarcell+1]:
			for x in list(range(map_width))[3:-3]:
				for fault in faultlines:
					if (abs((x-fault[0])**2 + (y-fault[1])**2 - \
						fault[2]**2) <= FAULT_WIDTH**2):
						elevationtiles[x + map_width * y] += ELEVATION_BUILD

		# spread the love
		newmap = elevationtiles[:]
		for y in range(map_height):
			for x in range(map_width):
				if (newmap[x + map_width * y] > 0):
					adjtiles = adjacenttiles(x, y)
					for adjtile in adjtiles:
						newmap[adjtile[0] + map_width * adjtile[1]] += \
							newmap[x + map_width * y] * ELEVATION_SPREAD
					newmap[x + map_width * y] *= ELEVATION_EROSION
		elevationtiles = newmap[:]

	#elevationtiles = [(int)(i) for i in elevationtiles]

def getwind(degrees):
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

def getcoastinfo(x, y):
	dist = 1
	waterfound = []

	while (dist<(map_width/2+1)):
		xplus = (x+dist)%map_width
		yplus = min((y+dist), map_height-1)
		if (worldtiles[xplus + map_width * y] == 'water'):
			waterfound.append(((1, 0), dist))
		if (worldtiles[x + map_width * yplus] == 'water'):
			waterfound.append(((0, 1), dist))

		xminus = (x+map_width-dist)%map_width
		yminus = max((y-dist), 0)
		if (worldtiles[xminus + map_width * y] == 'water'):
			waterfound.append(((-1, 0), dist))
		if (worldtiles[x + map_width * yminus] == 'water'):
			waterfound.append(((0, -1), dist))

		if (worldtiles[xplus + map_width * yplus] == 'water'):
			waterfound.append(((1, 1), dist+1))
		if (worldtiles[xplus + map_width * yminus] == 'water'):
			waterfound.append(((1, -1), dist+1))
		if (worldtiles[xminus + map_width * yplus] == 'water'):
			waterfound.append(((-1, 1), dist+1))
		if (worldtiles[xminus + map_width * yminus] == 'water'):
			waterfound.append(((-1, -1), dist+1))
		dist += 1

	return waterfound

def worldtile(x, y):
	try:
		result = worldtiles[x + map_width * y]
	except:
		print(len(worldtiles), x, y)
		input()
	return result

def gettilesbytype(*tiletypes):
	result = []
	for y in range(map_height):
		for x in range(map_width):
			if worldtile(x, y) in tiletypes:
				result.append((x, y))
	return result

def getrainshadow(x, y, degrees, wind, mountains):
	raindepth = 1

	northbounds = degrees - degrees%30
	southbounds = northbounds + 30
	wx, wy = wind

	#print(northbounds, southbounds, wx, wy, x, y)

	# follow wind vector backwards to check for mountain
	# stop when the wind cell ends, or when a mountain is found
	px = x-wx
	py = y-wy
	degrees = (int)((float)(py)/tilesperdegree)
	while (degrees >= northbounds and degrees < southbounds):
		if ((px, py) in mountains):
			raindepth -= 2 # shadow tiles per mountain width
		if (raindepth < 1):
			return True
		else:
			px = px-wx
			py = py-wy
			degrees = (int)((float)(py)/tilesperdegree)
			raindepth += 1

	return False

def defaultwater():
	global worldtiles
	worldtiles = ['water'] * map_width * map_height

def setterrain(x, y):
	global worldtiles

	if (elevationtiles[x + map_width * y] >= 1.0):
		worldtiles[x + map_width * y] = 'ground'
	if (elevationtiles[x + map_width * y] >= 3.5):
		worldtiles[x + map_width * y] = 'mountain'

def raisemountains():
	mountains = gettilesbytype('mountain')
	if (len(mountains) < MIN_MOUNTS):
		return False

	numpolars = 0

	# raise some mountain peaks
	# assumes MIN_MOUNTS > NUM_POLARS
	shuffle(mountains)
	for mt in mountains:
		if len(adjacenttiles(mt[0], mt[1], 
				diag=True, tiletypes=['mountain', 'polar'])) >= 6:
			worldtiles[mt[0] + map_width * mt[1]] = 'polar'	
			numpolars += 1

			if (numpolars >= NUM_POLARS):
				return True

	if (numpolars < NUM_POLARS):
		return False

def getcurrenttemp(degrees, coastinfo):
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


def getonshorewind(y, degrees, wind, coastinfo, rainshadow):
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
		coastdegrees = (int)((float)(y + direction[1]*dist)/tilesperdegree)
		# if in the same wind cell
		if (coastdegrees >= northbounds and coastdegrees <= southbounds):
			# if the coast is in the direciton the wind blows from
			if (direction == wind):
				return True

	return False

def dist2coast(coastinfo):
	if (coastinfo is None or len(coastinfo) <= 0):
		return None

	mindist = coastinfo[0][1]
	#mindirection = coastinfo[0][0]

	for direction, dist in coastinfo:
		if dist < mindist:
			mindist = dist
			#mindirection = direction

	return mindist

def setbiome(x, y, 
	degrees, dist2coast,
	coastinfo, currenttemp, 
	rainshadow, onshorewind):

	global worldtiles
	worldtiles[x + map_width * y] = 'ground'

	# HADLEY CELL
	if (degrees >= 80 and degrees <= 100 and
		onshorewind):
		worldtiles[x + map_width * y] = 'tropical rainforest'
	elif (degrees >= 70 and degrees <= 110 and 
		not rainshadow):
		worldtiles[x + map_width * y] = 'tropical savannah'
	elif (degrees >= 60 and degrees <= 120 and 
		onshorewind and
		dist2coast <= COASTAL_DIST and
		currenttemp == 'warm'):
		worldtiles[x + map_width * y] = 'tropical savannah'
	elif ((degrees <= 80 and degrees >= 60 or
		degrees <= 120 and degrees >= 100) and
		currenttemp != 'warm' and
		not onshorewind):
		worldtiles[x + map_width * y] = 'hot desert'
	elif (degrees <= 120 and degrees >= 60):
		worldtiles[x + map_width * y] = 'hot steppe'

	# FERREL CELL and POLAR CELL
	if ((degrees <= 150 and degrees >= 120 or
		degrees <= 60 and degrees >= 30)):
		worldtiles[x + map_width * y] = 'humid continental'
	# carve away at humid continental
	if ((degrees <= 160 and degrees >= 135 or
		degrees <= 45 and degrees >= 20)):
		worldtiles[x + map_width * y] = 'subarctic continental'
	# carve into more unique biomes
	if ((degrees <= 135 and degrees >= 120 or
		degrees <= 60 and degrees >= 45) and
		onshorewind and
		currenttemp == 'cold' and
		dist2coast < COASTAL_DIST):
		worldtiles[x + map_width * y] = 'mediterranean'
	elif ((degrees <= 135 and degrees >= 120 or
		degrees <= 60 and degrees >= 45) and
		onshorewind and
		currenttemp == 'warm' and
		dist2coast <= COASTAL_DIST):
		worldtiles[x + map_width * y] = 'humid subtropical'
	elif ((degrees <= 150 and degrees >= 130 or
		degrees <= 50 and degrees >= 30) and
		currenttemp == 'warm'):
		worldtiles[x + map_width * y] = 'oceanic'
	if ((degrees <= 135 and degrees >= 120 or
		degrees <= 60 and degrees >= 45) and
		onshorewind and
		currenttemp == 'warm' and
		dist2coast <= 1):
		if (choices([True, False], [0.5, 0.5])[0]):
			worldtiles[x + map_width * y] = 'coastal temp rainforest'
	if ((degrees <= 160 and degrees >= 120 or
		degrees <= 60 and degrees >= 20) and
		not onshorewind and
		dist2coast > COASTAL_DIST*1.5):
		worldtiles[x + map_width * y] = 'cold desert'
	# do cold step in setsteppes()
	if ((degrees <= 170 and degrees >= 150 or
		degrees <= 30 and degrees >= 10)):
		worldtiles[x + map_width * y] = 'tundra'
	elif ((degrees >= 175 or degrees <= 15)):
		worldtiles[x + map_width * y] = 'ice cap'

def setsteppes():
	global worldtiles
	newmap = worldtiles[:]
	for y in range(map_height):
		for x in range(map_width):
			adjtiles = adjacenttiles(x, y, False)
			adjtiles = [worldtile(*tile) for tile in adjtiles]
			if ('cold desert' in adjtiles and
				('humid continental' in adjtiles or
				'hot steppe' in adjtiles or
				'subarctic continental' in adjtiles)):
				FREQ = STEPPE_FREQ
				if (worldtile(x, y) == 'cold desert'):
					FREQ = 0
				if (choices([True, False], [STEPPE_FREQ, 1.0-STEPPE_FREQ])[0]):
					newmap[x + map_width * y] = 'cold steppe'
	for y in range(map_height):
		for x in range(map_width):
			adjtiles = adjacenttiles(x, y, False)
			adjtiles = [worldtile(*tile) for tile in adjtiles]
			if ('hot desert' in adjtiles and
				('tropical savannah' in adjtiles or
				'humid subtropical' in adjtiles or
				'humid continental' in adjtiles or
				'tropical rainforest' in adjtiles or
				'cold steppe' in adjtiles)):
				FREQ = STEPPE_FREQ
				if (worldtile(x, y) == 'hot desert'):
					FREQ = 0
				if (choices([True, False], [STEPPE_FREQ, 1.0-STEPPE_FREQ])[0]):
					newmap[x + map_width * y] = 'hot steppe'
	worldtiles = newmap

def generatebiomes():
	defaultwater()

	# map high altitude temps
	for y in range(map_height):
		for x in range(map_width):
			setterrain(x, y)

	if (raisemountains() == False):
		return False
	mountains = gettilesbytype('mountain', 'polar')

	for y in range(map_height):
		degrees = (int)((float)(y)/tilesperdegree)
		wind = getwind(degrees)
		ice_prob = 0.0
		if (degrees >= 165 or degrees < 10):
			ice_prob = 1.0-float(min(175-degrees, degrees))/10.0
		for x in range(map_width):
			if (worldtile(x, y) == 'ground'):
				adjtiles = adjacenttiles(x, y, True)
				coastinfo = getcoastinfo(x, y)
				nearestcoast = dist2coast(coastinfo)
				rainshadow = getrainshadow(x, y, degrees, wind, mountains)
				onshorewind = getonshorewind(y, degrees, wind, coastinfo, rainshadow)
				currenttemp = getcurrenttemp(degrees, coastinfo)
				setbiome(x, y, 
					degrees, nearestcoast,
					coastinfo, currenttemp,
					rainshadow, onshorewind)
			if (worldtile(x, y) == 'water'):
				if (choices([True, False], [ice_prob, 1.0-ice_prob])[0]):
					worldtiles[x + map_width * y] = 'ice cap'

	# transition from deserts into steppes
	setsteppes()

	return True

def generateworld(randomseed):
	coolworld = False

	while (not coolworld):
		generateelevation()
		coolworld = generatebiomes()
		if not coolworld:
			randomseed = randint(0, 2**15)
			seed(randomseed)

	print("world seed: %d" % randomseed)			

def printworld(con):
	for y in range(map_height):
		for x in range(map_width):
			printchar = '#'
			fgcolor = colors.get(worldtile(x, y))
			bgcolor = colors.get(worldtile(x, y))
			if (worldtile(x, y) == 'ice cap'):
				bgcolor = colors.get('water')
			elif (not worldtile(x, y) in ['water', 'mountain', 'polar']):
				bgcolor = colors.get('ground')
			if (worldtile(x, y) in ['polar', 'mountain']):
				printchar = '^'
				fgcolor = bgcolor * libtcod.grey
			if (worldtile(x, y) == 'water'):
				if (((x+y) % 7 == 0 or x % 9 == 1) and 
					(y % 5 == 0 or y % 8 == 1)):
					printchar = '~'
					fgcolor = libtcod.light_blue
			con.draw_rect(
				x+draw_offset_x, y+draw_offset_y, 
				1, 1,
				ord(printchar),
				fg=fgcolor,
				bg=bgcolor)
			
	libtcod.console_blit(
		con, 0, 0, screen_width, screen_height, 0, 0, 0)

'''
DOPE AS HELL SEEDS:

11684
22805
4629
32485
28848
27299
32676
28398
27592
19389

'''

def main():
	if len(sys.argv) > 1:
		randomseed = int(sys.argv[1])
		seed(randomseed)
	else:
		randomseed = randint(0, 2**15)
		seed(randomseed)

	libtcod.console_set_custom_font('arial10x10.png', 
		libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
	libtcod.console_init_root(screen_width, screen_height, 
		'libtcod tutorial revised', False, 
		libtcod.RENDERER_SDL2, vsync=True)
	con = libtcod.console.Console(screen_width, screen_height)
	printbiome = ''

	generateworld(randomseed)
	printworld(con)
	libtcod.console_flush()

	while True:
		for event in tcod.event.wait():
			if event.type == "QUIT":
				raise SystemExit()
			elif event.type == "MOUSEBUTTONDOWN":
				scrx, scry = event.tile
				mapx = scrx - draw_offset_x
				mapy = scry - draw_offset_y
				if (mapx >= 0 and
					mapx < map_width and
					mapy >= 0 and
					mapy < map_height):

					printbiome = worldtile(mapx, mapy) + ' '*50
					print(printbiome)
			elif event.type == "KEYDOWN":
				if event.sym == 27:
					raise SystemExit()
				elif event.sym == 13:
					randomseed = randint(0, 2**15)
					seed(randomseed)
					generateworld(randomseed)	
	
		#con.clear()
		printworld(con)
		con.print(
			1, screen_height-4, 
			printbiome,
			fg=libtcod.light_grey,
			alignment=libtcod.LEFT)
		libtcod.console_flush()

if __name__=='__main__':
	main()