import random

'''
a     b
 xy

c     d

0 <= x <= 1
0 <= y <= 1
'''

def bilinlerp(x, y, a, b, c, d):
	return (
		a * (1-x) * (1-y) +
		b * x * (1-y) +
		c * (1-x) * y +
		d * x * y
		)

def noisegrid(size=64, precision=4):
	GRID_WIDTH = GRID_HEIGHT = size
	SKELLYWIDTH = SKELLYHEIGHT = 2**precision

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

			result[x + GRID_WIDTH * y] = bilinlerp(
				wx, wy, skellya, skellyb, skellyc, skellyd)
	return result

def printgrid(grid):
	for y in range(GRID_HEIGHT):
		line = ','.join(
			['{0:.3f}'.format(x) for x in grid[y*GRID_WIDTH:(y+1)*GRID_WIDTH]])
		print('v' + str(y) + ' <- c(' + line + ')')
	print('result <- array(c(%s),dim = c(%d,%d))' % (
		','.join(['v%d'%i for i in range(GRID_HEIGHT)]),
		GRID_WIDTH,
		GRID_HEIGHT))

def main():
	while(1):
		seed = int(input("seed: "))
		random.seed(seed)
		grid = noisegrid()
		printgrid(grid)


if __name__=='__main__':
	main()