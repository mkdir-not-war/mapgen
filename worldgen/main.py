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
screen_height = 50

# Map panel parameters
map_width = 64
map_height = 40

draw_offset_x = (int)((screen_width - map_width) / 2)
draw_offset_y = (int)((screen_height - map_height) / 2)

def printworld(root, con, world):
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

def printregion(root, con, region):
	for y in range(region.height):
		for x in range(region.width):
			tile = region.regiontile(x, y)
			printchar = '+'
			fgcolor = None
			bgcolor = None
			if (tile.allwater):
				bgcolor = colors.get('water')
				if (((x+y) % 7 == 0 or x % 9 == 1) and 
					(y % 5 == 0 or y % 8 == 1)):
					printchar = '~'
					fgcolor = colors.get('waterfg')
			else:
				bgcolor = colors.get('ground')
			if fgcolor is None:
				fgcolor = bgcolor
			con.draw_rect(
				x+draw_offset_x, y+draw_offset_y, 
				1, 1,
				ord(printchar),
				fg=fgcolor,
				bg=bgcolor)
	
	con.blit(root)

def printUI(con, world, region, viewstate):
	if (viewstate == ViewState.REGION):
		con.print(
			4, 2, 
			region.biome,
			fg=libtcod.light_grey,
			alignment=libtcod.LEFT)

def main():
	if len(sys.argv) > 1:
		randomseed = int(sys.argv[1])
		seed(randomseed)

	p1 = NoiseGrid(size=64, precision=4)
	p2 = NoiseGrid(size=64, precision=4)
	p3 = NoiseGrid(size=64, precision=4)

	libtcod.console_set_custom_font('arial10x10.png', 
		libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
	root = libtcod.console_init_root(screen_width, screen_height, 
			'world gen', False, 
			libtcod.RENDERER_SDL2, vsync=True)
	con = libtcod.console.Console(screen_width, screen_height)
	printbiome = ''

	world = WorldMap(map_width, map_height)
	region = None
	printworld(root, con, world)
	libtcod.console_flush()

	viewstate = ViewState.WORLD

	while True:
		for event in tcod.event.wait():
			if event.type == "QUIT":
				raise SystemExit()

			elif viewstate == ViewState.WORLD:
				printworld(root, con, world)
				if event.type == "MOUSEBUTTONDOWN":
					scrx, scry = event.tile
					mapx = scrx - draw_offset_x
					mapy = scry - draw_offset_y
					tile = None
					if (mapx >= 0 and
						mapx < map_width and
						mapy >= 0 and
						mapy < map_height):

						if event.button == libtcod.event.BUTTON_LEFT:
							region = RegionMap(
								mapx, mapy, 
								world,
								[p1, p2, p3])
							viewstate = ViewState.REGION
						else:
							print(event.button)
				elif event.type == "KEYDOWN":
					if event.sym == libtcod.event.K_ESCAPE:
						raise SystemExit()
			elif viewstate == ViewState.REGION:
				printregion(root, con, region)
				if event.type == "MOUSEBUTTONDOWN":
					if event.button == "BUTTON_LEFT":
						pass
					elif event.button == "BUTTON_RIGHT":
						pass
				elif event.type == "KEYDOWN":
					if event.sym == libtcod.event.K_ESCAPE:
						viewstate = ViewState.WORLD
	
		con.clear()
		printUI(con, world, region, viewstate)
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