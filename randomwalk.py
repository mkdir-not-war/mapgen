height = 8
width = 18
avg_dist = int((width + height) / 2)
midpoint = (int(width/2), int(height/2))

fromdirdict = {
	(1, 0) : 2,
	(-1, 0) : 0,
	(0, 1) : 1,
	(0, -1) : 3
}

from random import choice

def tupleadd(t1, t2):
	result = (t1[0]+t2[0], t1[1]+t2[1])
	return result

def inbounds(newpos):
	result = (
		newpos[0] >= 0 and
		newpos[0] < width and
		newpos[1] >= 0 and
		newpos[1] < height)
	return result

def randomwalk(length):
	mapdict = {}
	# right, up, left, down
	possiblevecs = [(0, 1), (1, 0), (-1, 0), (0, -1)]
	fromdirection = None # 0=left, 1=down, 2=right, 3=up
	current = midpoint
	for i in range(length):
		if (current in mapdict and fromdirection != None):
			mapdict[current][fromdirection] = True # set exit from
		elif (not current in mapdict):
			mapdict[current] = [False, False, False, False]
			if (fromdirection != None):
				mapdict[current][fromdirection] = True # set exit from
		if (i % min(max(3, length/3), avg_dist) != 0):
			newdir = choice(possiblevecs)
			while (not inbounds(tupleadd(current, newdir))):
				newdir = choice(possiblevecs)
			fromdirection = fromdirdict[newdir]
			if (i < length-1):
				mapdict[current][(fromdirection+2)%4] = True # set exit to
			current = tupleadd(current, newdir)		
		else:
			fromdirection = None
			current = midpoint
	return mapdict

def printmap(mapdict):
	print("MAP: (%s rooms)" % len(mapdict.keys()))
	for y in range(height):
		topexitrow = []
		row = []
		botexitrow = []

		for x in range(width):
			if ((x,y) in mapdict):
				roomchar = '.'
				if ((x,y) == midpoint):
					roomchar = '@'
				exits = mapdict[(x, y)]
				if (exits[1]):
					topexitrow.append('  ^  ')
				else:
					topexitrow.append('     ')
				if (exits[3]):
					botexitrow.append('  v  ')
				else:
					botexitrow.append('     ')
				if (exits[0]):
					if (exits[2]):
						row.append(' <%s> ' % roomchar)
					else:
						row.append('  %s> ' % roomchar)
				else:
					if (exits[2]):
						row.append(' <%s  ' % roomchar)
					else:
						row.append('  %s  ' % roomchar)
			else:
				topexitrow.append('     ')
				row.append('     ')
				botexitrow.append('     ')


		print(''.join(topexitrow))
		print(''.join(row))
		print(''.join(botexitrow))
		print()
	print()

def main():
	length = 0
	while(1):
		userinput = input('length: ')
		if (userinput != ''):
			try:
				length = int(userinput)
			except ValueError:
				continue
		else:
			print('length: %s' % length)
		mapdict = randomwalk(length)
		printmap(mapdict)

if __name__=='__main__':
	main()