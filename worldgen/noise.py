import random
from pathfinding import manhattandist

def bilerp(x, y, a, b, c, d):
	return (
		a * (1-x) * (1-y) +
		b * x * (1-y) +
		c * (1-x) * y +
		d * x * y
		)

class NoiseGrid():
	def __init__(self, size=64, precision=4, gentiles=True):
		self.size = size
		self.amplitude = 1
		self.precision = precision

		self.tiles = []
		if (gentiles):
			self.tiles = self.generate()
		else:
			self.tiles = [0.0] * self.size**2

	def get(self, x, y):
		result = self.tiles[x + self.size * y]
		return result

	# assume same size & precision?
	def add(self, noisegrid):
		result = NoiseGrid(self.size, self.precision, False)
		for i in range(result.size**2):
			result.tiles[i] = self.tiles[i] + noisegrid.tiles[i]
		result.amplitude = self.amplitude + noisegrid.amplitude
		return result

	def scale(self, scalar):
		result = NoiseGrid(self.size, self.precision, False)
		for i in range(result.size**2):
			result.tiles[i] = self.tiles[i]*scalar
		result.amplitude = self.amplitude*scalar
		return result

	def sizedown(self, scalefactor):
		result = NoiseGrid(
			self.size//scalefactor, self.precision, False)

		GRID_WIDTH = GRID_HEIGHT = self.size

		result.tiles.clear()
		for y in list(range(GRID_HEIGHT))[::scalefactor]:
			for x in list(range(GRID_WIDTH))[::scalefactor]:
				result.tiles.append(
					self.tiles[x + self.size * y])

		return result

	def translate(self, x, y):
		# x, y is new top left
		result = NoiseGrid(self.size, self.precision, False)
		result.tiles = [0] * self.size**2
		for j in range(self.size):
			for i in range(self.size):
				val = self.tiles[((i+x)%self.size) + \
					self.size * ((j+y)%self.size)]
				result.tiles[i + self.size * j] = val
		return result

	def generate(self):
		GRID_WIDTH = GRID_HEIGHT = self.size
		SKELLYWIDTH = SKELLYHEIGHT = 2**self.precision

		skeleton = [None] * SKELLYWIDTH * SKELLYHEIGHT
		result = [None] * GRID_WIDTH * GRID_HEIGHT
		tilesperskelly = (GRID_WIDTH/SKELLYWIDTH, GRID_HEIGHT/SKELLYHEIGHT)
		for i in range(len(skeleton)):
			skeleton[i] = random.random()
		for y in range(GRID_HEIGHT):
			for x in range(GRID_WIDTH):
				skellyx = int(x / tilesperskelly[0])
				skellyxplus = (skellyx+1)%SKELLYWIDTH
				wx = float(x%tilesperskelly[0]) / tilesperskelly[0]

				skellyy = int(y / tilesperskelly[1])
				skellyyplus = (skellyy+1)%SKELLYHEIGHT
				wy = float(y%tilesperskelly[1]) / tilesperskelly[1]

				skellya = skeleton[skellyx + SKELLYWIDTH * skellyy]
				skellyb = skeleton[skellyxplus + SKELLYWIDTH * skellyy]
				skellyc = skeleton[skellyx + SKELLYWIDTH * skellyyplus]
				skellyd = skeleton[skellyxplus + SKELLYWIDTH * skellyyplus]

				result[x + GRID_WIDTH * y] = bilerp(
					wx, wy, skellya, skellyb, skellyc, skellyd)
		return result

	def extremes(self, mindist=1, buffer=1, minmax='max', num=1):
		result = []
		sortednoise = []

		for y in range(self.size):
			for x in range(self.size):
				if (x+buffer < self.size and
					x-buffer >= 0 and
					y+buffer < self.size and
					y-buffer >= 0):
					sortednoise.append((self.get(x, y), (x, y)))

		sortednoise = sorted(
			sortednoise, key=lambda x: x[0], reverse=(minmax=='max'))

		#threshold = 0.8
		#sortednoise = filter(
		#	lambda x: x[0]/self.amplitude>=threshold, 
		#	sortednoise)

		index = 0
		while (len(result) < num):
			val, pos = sortednoise[index]
			tooclose = False
			for pos2 in result:
				if manhattandist(pos, pos2) <= buffer or tooclose:
					tooclose = True
			if not tooclose:
				result.append(pos)
			index += 1

		return result

############################# DEBUG STUFF ###############

# print R code
def printgridcode(grid):
	GRID_WIDTH = GRID_HEIGHT = grid.size
	for y in range(GRID_HEIGHT):
		line = ','.join(
			['{0:.3f}'.format(x) \
				for x in grid.tiles[y*GRID_WIDTH:(y+1)*GRID_WIDTH]])
		print('v' + str(y) + ' <- c(' + line + ')')
	print('result <- array(c(%s),dim = c(%d,%d))' % (
		','.join(['v%d'%i for i in range(GRID_HEIGHT)]),
		GRID_WIDTH,
		GRID_HEIGHT))
	print('image(result)')

def printgrid(grid):
	GRID_WIDTH = GRID_HEIGHT = grid.size
	for y in range(GRID_HEIGHT):
		line = ' '.join(
			['{0:.1f}'.format(x) \
				for x in grid.tiles[y*GRID_WIDTH:(y+1)*GRID_WIDTH]])
		print(line)
	print()

def main():
	while(1):
		seed = int(input("seed: "))
		random.seed(seed)
		grid = NoiseGrid(32, 3)
		printgridcode(grid)
		grid16 = grid.sizedown(2)
		printgridcode(grid16)


if __name__=='__main__':
	main()

############################################