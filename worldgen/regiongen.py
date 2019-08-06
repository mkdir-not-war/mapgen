import sys
import tcod as libtcod
import tcod.event
from random import random, choice, choices, randint, seed, shuffle
from numpy import multiply

def colormult(c1, c2):
	result = tuple(multiply(c1, c2) // 255)
	return result

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

colors = {
	'black': libtcod.black,
	'ground': libtcod.Color(204, 120, 96),
	'mountain': libtcod.Color(179, 51, 16),
	'water': colormult(libtcod.desaturated_blue, libtcod.lighter_grey),
	'polar': colormult(libtcod.lightest_blue, libtcod.white),

	'tropical rainforest': libtcod.darker_green,	
	'tropical savannah': colormult(
		libtcod.gold, libtcod.lighter_chartreuse),	
	'hot desert': libtcod.gold,	
	'hot steppe': colormult(libtcod.red, libtcod.gold),	

	'humid continental': colormult(
		libtcod.Color(143, 181, 100), libtcod.lightest_grey),	
	'subarctic continental': colormult(
		libtcod.Color(143, 181, 100), libtcod.grey),	
	'mediterranean': libtcod.purple,	
	'humid subtropical': colormult(
		libtcod.purple, libtcod.lighter_blue),	
	'oceanic': libtcod.dark_orange,	
	'coastal temp rainforest': libtcod.darker_purple,
	'cold desert': colormult(libtcod.gold, libtcod.lightest_grey),	
	'cold steppe': colormult(libtcod.light_red, libtcod.lighter_blue),	

	'tundra': colormult(libtcod.lightest_blue, libtcod.lighter_grey),	
	'ice cap': colormult(libtcod.lightest_blue, libtcod.white),
	'volcano': libtcod.red
}

screen_width = 80 # /4 = 20
screen_height = 50 # /4 ~= 12

# Map panel parameters
map_width = 64
map_height = 40

draw_offset_x = (int)((screen_width - map_width) / 2)
draw_offset_y = (int)((screen_height - map_height) / 2)

regiontiles = []
pointsofinterest = {}

def generateregion(biome, p1, p2, p3):
	'''
	coolworld = False

	while (not coolworld):
		generateelevation()
		coolworld = generatebiomes()
		if not coolworld:
			randomseed = randint(0, 2**15)
			seed(randomseed)

	return randomseed	
	'''
	pass		

def printregion(con):
	for y in range(map_height):
		for x in range(map_width):
			pass
			'''
			printchar = '#'
			fgcolor = colors.get(worldtile(x, y))
			bgcolor = colors.get(worldtile(x, y))
			if (worldtile(x, y) == 'ice cap'):
				bgcolor = colors.get('water')
			elif (not worldtile(x, y) in ['water', 'mountain', 'polar']):
				bgcolor = colors.get('ground')
			if (worldtile(x, y) in ['polar', 'mountain']):
				printchar = '^'
				fgcolor = colormult(bgcolor, libtcod.grey)
			if (worldtile(x, y) == 'volcano'):
				printchar = '^'
				bgcolor = colors.get('mountain')
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
			'''
	
	libtcod.console_blit(
		con, 0, 0, screen_width, screen_height, 0, 0, 0)

	#con.blit(con, fg_alpha=0, bg_alpha=0)

def printinfo(con, seed):
	con.print(
		4, 2, 
		"region seed: %d      " % seed,
		fg=libtcod.light_grey,
		alignment=libtcod.LEFT)

def main():
	if len(sys.argv) > 1:
		randomseed = int(sys.argv[1])
		seed(randomseed)
	else:
		randomseed = randint(0, 2**15)
		seed(randomseed)
		print(randomseed)

	libtcod.console_set_custom_font('arial10x10.png', 
		libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
	libtcod.console_init_root(screen_width, screen_height, 
		'libtcod tutorial revised', False, 
		libtcod.RENDERER_SDL2, vsync=True)
	con = libtcod.console.Console(screen_width, screen_height)

	biome = choice(biomes)

	generateregion(biome, p1, p2, p3)
	printregion(con)
	printinfo(con, printseed)
	libtcod.console_flush()

	while True:
		for event in tcod.event.wait():
			if event.type == "QUIT":
				raise SystemExit()
			elif event.type == "KEYDOWN":
				if event.sym == 27:
					raise SystemExit()
				elif event.sym == 13:
					randomseed = randint(0, 2**15)
					seed(randomseed)
					generateregion(biome, p1, p2, p3)

		printregion(con)
		printinfo(con)
		libtcod.console_flush()

if __name__=='__main__':
	main()