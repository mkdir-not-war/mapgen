import sys
import tcod as libtcod
import tcod.event
from random import random, choice, choices, randint, seed, shuffle

colors = {
	'black': libtcod.black,
	'ground': libtcod.Color(204, 120, 96),
	'mountain': libtcod.Color(179, 51, 16),
	'water': libtcod.desaturated_blue * libtcod.lighter_grey,

	'tropical rainforest': libtcod.Color(143, 181, 100),	
	'tropical savannah': libtcod.Color(143, 181, 100),	
	'hot desert': libtcod.Color(143, 181, 100),	
	'hot steppe': libtcod.Color(143, 181, 100),	

	'humid continental': libtcod.Color(143, 181, 100),	
	'subarctic continental': libtcod.Color(143, 181, 100),	
	'mediterranean': libtcod.Color(143, 181, 100),	
	'humid subtropical': libtcod.Color(143, 181, 100),	
	'oceanic': libtcod.Color(143, 181, 100),	
	'coastal temp rainforest': libtcod.Color(143, 181, 100),
	'cold desert': libtcod.Color(143, 181, 100),	
	'cold steppe': libtcod.Color(143, 181, 100),	

	'tundra': libtcod.lightest_blue * libtcod.lighter_grey,	
	'polar': libtcod.lightest_blue * libtcod.white
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
		for y in list(range(map_height))[npolarcell:spolarcell]:
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

def getnearestcoast(x, y):
	dist = 1
	waterfound = False

	#ewtiles = worldtiles[y*map_width:(y+1)*map_width]

	# assumes there exists water on every row
	while (not waterfound and dist<(map_width/2+1)):
		xplus = (x+dist)%map_width
		if (worldtiles[xplus + map_width * y] == 'water'):
			waterfound = 'east'
		xminus = (x+map_width-dist)%map_width
		if (worldtiles[xminus + map_width * y] == 'water'):
			waterfound = 'west'
		dist += 1

	return waterfound, dist

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
	result = False

	northbounds = degrees - degrees%30
	southbounds = northbounds + 30
	wx, wy = wind

	# follow wind vector backwards to check for mountain
	# stop when the wind cell ends, or when a mountain is found
	px = x-wx
	py = y-wy
	while (py <= northbounds and py >= southbounds and result == False):
		if ((px, py) in mountains):
			result = True
		else:
			px = px-wx
			py = py-wy

	return result

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

def generatebiomes():
	defaultwater()

	# map high altitude temps
	for y in range(map_height):
		for x in range(map_width):
			setterrain(x, y)

	if (raisemountains() == False):
		return False
	mountains = gettilesbytype('mountain')

	for y in range(map_height):
		degrees = (int)((float)(y)/tilesperdegree)
		wind = getwind(degrees)
		for x in range(map_width):
			if (worldtile(x, y) == 'ground'):
				adjtiles = adjacenttiles(x, y, True)
				coast, dist2coast = getnearestcoast(x, y)
				rainshadow = getrainshadow(x, y, degrees, wind, mountains)

	return True

def generateworld(randomseed):
	coolworld = False

	while (not coolworld):
		generateelevation()
		coolworld = generatebiomes()
		if not coolworld:
			print("world not cool enough...")
			randomseed = randint(0, 2**15)
			seed(randomseed)

	print("world seed: %d" % randomseed)
				

def printworld(con):
	for y in range(map_height):
		for x in range(map_width):
			con.draw_rect(
				x+draw_offset_x, y+draw_offset_y, 
				1, 1,
				ord('.'),
				fg=colors.get(worldtile(x, y)),
				bg=colors.get(worldtile(x, y)))
			
	libtcod.console_blit(
		con, 0, 0, screen_width, screen_height, 0, 0, 0)

'''
DOPE AS HELL SEEDS:


'''

def main():
	if len(sys.argv) > 1:
		print("world seed: %d" % int(sys.argv[1]))
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
	key = libtcod.Key()
	mouse = libtcod.Mouse()

	generateworld(randomseed)

	while True:
		printworld(con)
		libtcod.console_flush()

		for event in tcod.event.wait(0):
			if event.type == "QUIT":
				raise SystemExit()
			elif event.type == "KEYDOWN":
				if event.sym == 27:
					raise SystemExit()
				elif event.sym == 13:
					generateworld(randomseed)	


if __name__=='__main__':
	main()