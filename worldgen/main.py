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

draw_offset_x = 0
draw_offset_y = 0

# Map panel parameters (and world size)
map_width = 64
map_height = 40

draw_offset_x = 0
draw_offset_y = 0

# Region size
regionside = 32

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

def printregion(root, con, region, adjregions):
	for y in range(region.height):
		for x in range(region.width):
			tiles = {}
			tiles[(0, 0)] = region.regiontile(x, y)
			for regdir in adjregions:
				tiles[regdir] = adjregions[regdir].regiontile(x, y)

			printchar = '+'
			fgcolor = None
			bgcolor = None
			for regdir in tiles:
				tile = tiles[regdir]
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
				drawpos = (
					x + draw_offset_x + regdir[0]*regionside, 
					y + draw_offset_y + regdir[1]*regionside)
				if (drawpos[0] >= 0 and 
					drawpos[1] >= 0 and
					drawpos[0] < screen_width and
					drawpos[1] < screen_height):
					con.draw_rect(
						drawpos[0], 
						drawpos[1],  
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

			elif viewstate == ViewState.WORLD:
				draw_offset_x = (int)((screen_width - map_width) / 2)
				draw_offset_y = (int)((screen_height - map_height) / 2)

				printworld(root, con, world)
				if event.type == "MOUSEBUTTONDOWN":
					scrx, scry = event.tile
					mapx = scrx - draw_offset_x
					mapy = scry - draw_offset_y
					if (mapx >= 0 and
						mapx < map_width and
						mapy >= 0 and
						mapy < map_height):

						if event.button == libtcod.event.BUTTON_LEFT:
							region = RegionMap(
								mapx, mapy, 
								world,
								noisegrids,
								regionside=regionside)
							viewstate = ViewState.REGION
						else:
							print(event.button)
				elif event.type == "KEYDOWN":
					if event.sym == libtcod.event.K_ESCAPE:
						raise SystemExit()
			elif viewstate == ViewState.REGION:
				draw_offset_x = (int)((screen_width - regionside) / 2)
				draw_offset_y = (int)((screen_height - regionside) / 2)

				printregion(root, con, region, adjregions)
				if event.type == "MOUSEBUTTONDOWN":
					scrx, scry = event.tile
					mapx = scrx - draw_offset_x
					mapy = scry - draw_offset_y
					if (mapx >= 0 and
						mapx < regionside and
						mapy >= 0 and
						mapy < regionside):

						if event.button == libtcod.event.BUTTON_LEFT:
							pass
						elif event.button == libtcod.event.BUTTON_RIGHT:
							newadj = {}
							cx, cy = (regionside//2, regionside//2)
							x, y = region.worldpos
							if (mapx < cx):
								if ((-1, 0) in adjregions):
									newadj[(-1, 0)] = \
										adjregions[(-1, 0)]
								else:
									newadj[(-1, 0)] = \
										RegionMap(
											x-1, y, 
											world,
											noisegrids,
											regionside=regionside)
							if (mapx >= cx):
								if ((1, 0) in adjregions):
									newadj[(1, 0)] = \
										adjregions[(1, 0)]
								else:
									newadj[(1, 0)] = \
										RegionMap(
											x+1, y, 
											world,
											noisegrids,
											regionside=regionside)
							if (mapy < cy):
								if ((0, -1) in adjregions):
									newadj[(0, -1)] = \
										adjregions[(0, -1)]
								else:
									newadj[(0, -1)] = \
										RegionMap(
											x, y-1, 
											world,
											noisegrids,
											regionside=regionside)
							if (mapy >= cy):
								if ((0, 1) in adjregions):
									newadj[(0, 1)] = \
										adjregions[(0, 1)]
								else:
									newadj[(0, 1)] = \
										RegionMap(
											x, y+1, 
											world,
											noisegrids,
											regionside=regionside)
							adjregions.clear()
							for key in newadj:
								adjregions[key] = newadj[key]

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