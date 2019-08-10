from numpy import multiply
import tcod as libtcod

def colormult(c1, c2):
	result = tuple(multiply(c1, c2) // 255)
	return result

colors = {
	'black': libtcod.black,
	'white': libtcod.white,
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
	'volcano': libtcod.red,

	'waterfg': libtcod.light_blue

}