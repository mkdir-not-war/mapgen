import sys
import tcod as libtcod
import tcod.event
from random import seed
from enum import Enum

from color import colors, colormult
from worldmap import WorldMap
from regionmap import RegionMap
from noise import NoiseGrid

class ViewState(Enum):
	WORLD = 1
	REGION = 2

screen_width = 80
screen_height = 80

draw_offset_x = 0
draw_offset_y = 0

# Map panel parameters (and world size)
map_width = 64
map_height = 40

draw_offset_x = 0
draw_offset_y = 0

# Region size
regionside = 32

def drawgame(root, con, world):
	for y in range(world.map_height):
		for x in range(world.map_width):
			tile = world.worldtile(x, y)
			printchar = '#'
			fgcolor = colors.get(tile.biome)
			bgcolor = colors.get(tile.biome)
			if (tile.biome == 'ice cap'):
				bgcolor = colors.get('water')
			elif (not tile.biome in ['water', 'mountain', 'polar']):
				bgcolor = colors.get('ground')
			if (tile.biome in ['polar', 'mountain']):
				printchar = '^'
				fgcolor = colormult(bgcolor, libtcod.grey)
			if (tile.biome == 'volcano'):
				printchar = '^'
				bgcolor = colors.get('mountain')
			if (tile.biome == 'water'):
				if (((x+y) % 7 == 0 or x % 9 == 1) and 
					(y % 5 == 0 or y % 8 == 1)):
					printchar = '~'
					fgcolor = colors.get('waterfg')
			con.draw_rect(
				x+draw_offset_x, y+draw_offset_y, 
				1, 1,
				ord(printchar),
				fg=fgcolor,
				bg=bgcolor)

	con.blit(root)

def printUI(con, world, region, viewstate):
	pass
	# draw player on top of everything

def main():
	if len(sys.argv) > 1:
		randomseed = int(sys.argv[1])
		seed(randomseed)

	global draw_offset_x
	global draw_offset_y

	p1 = NoiseGrid(size=64, precision=4)
	p2 = NoiseGrid(size=64, precision=4)
	p3 = NoiseGrid(size=64, precision=4)
	noisegrids = [p1, p2, p3]

	libtcod.console_set_custom_font('arial10x10.png', 
		libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
	root = libtcod.console_init_root(screen_width, screen_height, 
			'world gen', False, 
			libtcod.RENDERER_SDL2, vsync=True)
	con = libtcod.console.Console(screen_width, screen_height)
	printbiome = ''

	world = WorldMap(map_width, map_height)
	region = None
	adjregions = {}
	draw_offset_x = (int)((screen_width - map_width) / 2)
	draw_offset_y = (int)((screen_height - map_height) / 2)
	printworld(root, con, world)
	libtcod.console_flush()

	viewstate = ViewState.WORLD

	while True:
		for event in tcod.event.wait():
			if event.type == "QUIT":
				raise SystemExit()
	
		# print canvas
		con.clear()
		#printUI(con, world, region, viewstate)
		libtcod.console_flush()

if __name__=='__main__':
	main()

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
11655

'''