import tcod as libtcod
from random import random, choice, randint, seed

colors = {
	'ground': libtcod.Color(204, 120, 96),
	'mountain': libtcod.Color(179, 51, 16),
	'tree': libtcod.Color(143, 181, 100),
	'water': libtcod.desaturated_blue * libtcod.lighter_grey,
	'polar': libtcod.lightest_blue * libtcod.white,
	'black': libtcod.black
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

interval = (int)(map_height/6)
npolarcell = interval
nmidcell = interval*2
smidcell = map_height-interval*2
spolarcell = map_height-interval

NUMFAULTS = 28
SMALLRADIUS = 1
BIGRADIUS = 10
FAULT_WIDTH = 2
ELEVATION_GENS = 6
ELEVATION_BUILD = 1.01
ELEVATION_SPREAD = 0.23
ELEVATION_EROSION = 0.004
# 8, 20, 100, 2, 5, 1.0, 0.25, 0.18
# 14, 4, 100, 3, 6, 1.0, 0.23, 0.004

def adjacenttiles(x, y, diag=False):
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
			for x in range(map_width):
				for fault in faultlines:
					if (abs((x-fault[0])**2 + (y-fault[1])**2 - \
						fault[2]**2) <= FAULT_WIDTH**2):
						elevationtiles[x + map_width * y] += ELEVATION_BUILD

		# spread the love
		newmap = elevationtiles[:]
		for y in range(map_height):
			for x in range(map_width):
				if (newmap[x + map_width * y] > 0):
					adjtiles = adjacenttiles(x, y, False)
					for adjtile in adjtiles:
						newmap[adjtile[0] + map_width * adjtile[1]] += \
							newmap[x + map_width * y] * ELEVATION_SPREAD
					newmap[x + map_width * y] *= ELEVATION_EROSION
		elevationtiles = newmap[:]

	#elevationtiles = [(int)(i) for i in elevationtiles]

def generatebiomes():
	global worldtiles
	worldtiles = ['water'] * map_width * map_height
	for y in range(map_height):
		for x in range(map_width):
			if (elevationtiles[x + map_width * y] >= 1):
				worldtiles[x + map_width * y] = 'ground'
			if (elevationtiles[x + map_width * y] >= 4):
				worldtiles[x + map_width * y] = 'mountain'
			if (elevationtiles[x + map_width * y] >= 6):
				worldtiles[x + map_width * y] = 'polar'

def printworld(con):
	for y in range(map_height):
		for x in range(map_width):
			libtcod.console_set_char_background(
				con, 
				x+draw_offset_x, y+draw_offset_y, 
				colors.get(worldtiles[x + map_width * y]), 
				libtcod.BKGND_SET)
			libtcod.console_set_char_background(
				con, 
				x+draw_offset_x+map_width, y+draw_offset_y, 
				colors.get(worldtiles[x + map_width * y]), 
				libtcod.BKGND_SET)
			libtcod.console_set_char_background(
				con, 
				x+draw_offset_x-map_width, y+draw_offset_y, 
				colors.get(worldtiles[x + map_width * y]), 
				libtcod.BKGND_SET)
	libtcod.console_blit(
		con, 0, 0, screen_width, screen_height, 0, 0, 0)


def main():
	libtcod.console_init_root(screen_width, screen_height, 
		'libtcod tutorial revised', False, 
		libtcod.RENDERER_SDL2, vsync=True)
	con = libtcod.console.Console(screen_width, screen_height)
	key = libtcod.Key()
	mouse = libtcod.Mouse()

	generateelevation()
	generatebiomes()

	while not libtcod.console_is_window_closed():
		libtcod.sys_check_for_event(
			libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, 
			key, mouse)
		key_char = chr(key.c)
		if key.vk == libtcod.KEY_ESCAPE:
			return True

		if key.vk == libtcod.KEY_ENTER:
			generateelevation()
			generatebiomes()

		printworld(con)
		libtcod.console_flush()


if __name__=='__main__':
	main()