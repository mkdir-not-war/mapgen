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
	def __init__(self, size=64, precision=4):
		self.size = size
		self.amplitude = 1
		self.precision = precision
		self.tiles = self.generate()

	def get(self, x, y):
		result = self.tiles[x + self.size * y]
		return result

	# assume same size & precision?
	def add(self, noisegrid):
		result = NoiseGrid(self.size, self.precision)
		for i in range(result.size**2):
			result.tiles[i] = self.tiles[i] + noisegrid.tiles[i]
		result.amplitude = self.amplitude + noisegrid.amplitude
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

		sortednoise = sorted(sortednoise, key=lambda x: x[0], reverse=(minmax=='max'))

		#threshold = 0.8
		#sortednoise = filter(lambda x: x[0]/self.amplitude>=threshold, sortednoise)

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

###################################################### DEBUG STUFF ###############

# print R code
def printgrid(grid):
	GRID_WIDTH = GRID_HEIGHT = grid.size
	for y in range(GRID_HEIGHT):
		line = ','.join(
			['{0:.3f}'.format(x) for x in grid.tiles[y*GRID_WIDTH:(y+1)*GRID_WIDTH]])
		print('v' + str(y) + ' <- c(' + line + ')')
	print('result <- array(c(%s),dim = c(%d,%d))' % (
		','.join(['v%d'%i for i in range(GRID_HEIGHT)]),
		GRID_WIDTH,
		GRID_HEIGHT))
	print('image(result)')

def main():
	while(1):
		seed = int(input("seed: "))
		random.seed(seed)
		grid = NoiseGrid(16, 3)
		grid2 = NoiseGrid(16, 3)
		sumgrid = grid.add(grid2)
		printgrid(sumgrid)
		print()

		ext = sumgrid.extremes(minmax='min', mindist=4, buffer=2, num=4)
		for x, y in ext:
			print(str(grid.get(x, y)) + '\t' + str((x, y)))



if __name__=='__main__':
	main()

#####################################################################################