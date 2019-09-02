class LocalTile:
	def __init__(self):
		self.ground = True # default to ground
		self.road = False

		self.waterdir = False # stuff will float in this direction
		self.elevationdir = False # impassable
		self.ledgedir = False # one-way

	# trees and buildings are map objects, not captured in the tile

LOCALMAP_WIDTH = 64

class LocalMap:
	def __init__(self, x, y, region):
		regiontile = region.regiontile(x, y)

		self.tiles = []
		for x in range(LOCALMAP_WIDTH):
			for y in range(LOCALMAP_WIDTH):
				self.tiles[x + LOCALMAP_WIDTH * y] = LocalTile()

		self.mapobjects


	def localtile(self, x, y):
		pass

def main():
	pass

if __name__=='__main__':
	main()