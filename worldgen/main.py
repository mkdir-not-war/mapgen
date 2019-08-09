import sys
import tcod as libtcod
import tcod.event

from color import colors, colormult
from worldmap import WorldMap

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

def main():
	if len(sys.argv) > 1:
		randomseed = int(sys.argv[1])
		seed(randomseed)

	libtcod.console_set_custom_font('arial10x10.png', 
		libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
	root = libtcod.console_init_root(screen_width, screen_height, 
			'world gen', False, 
			libtcod.RENDERER_SDL2, vsync=True)
	con = libtcod.console.Console(screen_width, screen_height)
	printbiome = ''

	world = WorldMap(map_width, map_height)
	printworld(root, con, world)
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

					printbiome = world.worldtile(mapx, mapy).biome + ' '*50
			elif event.type == "KEYDOWN":
				if event.sym == 27:
					raise SystemExit()
	
		printworld(root, con, world)
		con.clear()
		con.print(
			4, screen_height-3, 
			printbiome,
			fg=libtcod.light_grey,
			alignment=libtcod.LEFT)
		libtcod.console_flush()

if __name__=='__main__':
	main()