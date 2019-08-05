import tcod as libtcod

libtcod.console_set_custom_font('arial10x10.png', 
	libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(screen_width, screen_height, 
	'libtcod tutorial revised', False, 
	libtcod.RENDERER_SDL2, vsync=True)
con = libtcod.console.Console(screen_width, screen_height)

'''
libtcod.console_set_char_background(con, x, y, libtcod.yellow, libtcod.BKGND_SET)
libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)
libtcod.console_flush()
'''