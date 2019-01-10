import random
from math import sqrt

water = '~'
wall = '#'
ground = '.'
stairs = '>'
ruin = 'x'
tree = 'F'

movecost = {}
movecost[ground] = 1
movecost[stairs] = 1
movecost[ruin] = 2
movecost[tree] = 2

traversable = [ground, stairs, ruin, tree]

#width = 150; height = 40
#width = 70; height = 35
width = 40; height = 20
size = width * height

class tilemap:
    def __init__(self):
        self.tiles = ['#'] * size
        self.s1 = (0, 0)
        self.s2 = (0, 0)

    def copy(self):
        newmap = tilemap()
        for i in range(size):
            newmap.tiles[i] = self.tiles[i]
            newmap.s1 = self.s1
            newmap.s2 = self.s2
        return newmap

    def settile(self, point, value):
        self.tiles[point[1] * width + point[0]] = value

    def gettile(self, x, y):
        return self.tiles[y * width + x]

    def getgroundtiles(self):
        result = []
        for i in range(width):
            for j in range(height):
                point = tuple([i, j])
                if (self.gettile(*point) == ground):
                    result.append(point)
        return result

    def setstair(self, num, point):
        if (num == 1):
            if (self.gettile(*self.s1) == stairs):
                self.settile(self.s1, ground)
            self.s1 = point
        elif (num == 2):
            if (self.gettile(*self.s2) == stairs):
                self.settile(self.s2, ground)
            self.s2 = point
        else:
            return
        self.settile(point, stairs)

def inbounds(x, y, buffer=0):
    return (x < width - buffer and
            x >= buffer and
            y < height - buffer and
            y >= buffer)

def adjacenttile(point, tiletype, worldmap, buffer=0):
    result = []
    x = point[0]
    y = point[1]

    if (inbounds(x-1, y, buffer) and
        worldmap.gettile(x-1, y) == tiletype):
        result.append(tuple([x-1, y]))
    if (inbounds(x+1, y, buffer) and
        worldmap.gettile(x+1, y) == tiletype):
        result.append(tuple([x+1, y]))
        
    if (inbounds(x, y-1, buffer) and
        worldmap.gettile(x, y-1) == tiletype):
        result.append(tuple([x, y-1]))
    if (inbounds(x, y+1, buffer) and
        worldmap.gettile(x, y+1) == tiletype):
        result.append(tuple([x, y+1]))
        
    if (inbounds(x-1, y-1, buffer) and
        worldmap.gettile(x-1, y-1) == tiletype):
        result.append(tuple([x-1, y-1]))
    if (inbounds(x-1, y+1, buffer) and
        worldmap.gettile(x-1, y+1) == tiletype):
        result.append(tuple([x-1, y+1]))
    if (inbounds(x+1, y-1, buffer) and
        worldmap.gettile(x+1, y-1) == tiletype):
        result.append(tuple([x+1, y-1]))
    if (inbounds(x+1, y+1, buffer) and
        worldmap.gettile(x+1, y+1) == tiletype):
        result.append(tuple([x+1, y+1]))

    #print(point, len(result), result)
    #input()

    return len(result)



def manhattandist(a, b):
    result = abs(a[0] - b[0]) + abs(a[1] - b[1])
    return result

def h(start, goal):
    return manhattandist(start, goal)

def tupleequal(x, y):
    return x[0] == y[0] and x[1] == y[1]

def neighbors(p, worldmap, travonly=True, buffer=1):
    x = p[0]
    y = p[1]
    result = []
    if (x - 1 >= buffer):
        if (not travonly or worldmap.gettile(x-1, y) in traversable):
            result.append(tuple([x-1, y]))
    if (x + 1 < width - buffer):
        if (not travonly or worldmap.gettile(x+1, y) in traversable):
            result.append(tuple([x+1, y]))
    if (y - 1 >= buffer):
        if (not travonly or worldmap.gettile(x, y-1) in traversable):
            result.append(tuple([x, y-1]))
    if (y + 1 < height - buffer):
        if (not travonly or worldmap.gettile(x, y+1) in traversable):
            result.append(tuple([x, y+1]))
    return result

def astar(start, goal, worldmap):
    closedset = []
    openset = [start]
    camefrom = {}
    gScore = {}
    gScore[start] = 0
    fScore = {}
    fScore[start] = h(start, goal)

    while openset:
        currenti = 0
        for p in range(len(openset)):
            if (openset[p] in fScore):
                if (fScore[openset[p]] < currenti):
                    currenti = p
        if tupleequal(openset[currenti], goal):
            return gScore[goal]
        current = openset[currenti]
        openset = openset[:currenti] + openset[currenti+1:]
        closedset.append(current)

        for n in neighbors(current, worldmap):
            if n in closedset:
                continue
            if n not in gScore:
                gScore[n] = height * width * 10
            t_gScore = gScore[current] + movecost[worldmap.gettile(*n)]
            if n not in openset:
                openset.append(n)
            elif t_gScore >= gScore[n]:
                continue
            camefrom[n] = current
            gScore[n] = t_gScore
            fScore[n] = t_gScore + h(n, goal)
    return -1

def cellularautomata():
    newmap = tilemap()

    scalemod = size / 1600 

    percentwalls=.32
    percentwalls += 0.01 * scalemod
    
    percentwater=.006
    lakesize=0.7
    
    percenttrees=.005
    forestsize=0.6
    
    percentruins=.003
    percentruins += 0.0025 * scalemod
    ruinsize=0.1
    
    gens = 3

    # walls
    for i in range(1, width-1):
        for j in range(1, height-1):
            newmap.settile(tuple([i, j]), ground)
            if ((j == height / 2 and
                 random.random() < percentwalls * 1.5) or
                random.random() < percentwalls):
                newmap.settile(tuple([i, j]), wall)

    for g in range(gens):
        oldmap = newmap.copy()
        for i in range(1, width-1):
            for j in range(1, height-1):
                point = tuple([i, j])
                adjwalls = adjacenttile(point, wall, oldmap)
                if (adjwalls >= 4):
                    newmap.settile(point, wall)
                else:
                    newmap.settile(point, ground)

    # water
    for i in range(1, width-1):
        for j in range(1, height-1):
            if (random.random() < percentwater and
                newmap.gettile(i, j) == wall):
                newmap.settile(tuple([i, j]), water)

    for g in range(gens):
        oldmap = newmap.copy()
        for i in range(1, width-1):
            for j in range(1, height-1):
                point = tuple([i, j])
                adjwater = adjacenttile(point, water, oldmap)
                if (adjwater > 0 and
                    random.random() < lakesize and
                    not oldmap.gettile(i, j) == ground):
                    newmap.settile(point, water)

    # trees
    for i in range(1, width-1):
        for j in range(1, height-1):
            if (random.random() < percenttrees and
                newmap.gettile(i, j) == ground):
                newmap.settile(tuple([i, j]), tree)

    for g in range(gens):
        oldmap = newmap.copy()
        for i in range(1, width-1):
            for j in range(1, height-1):
                point = tuple([i, j])
                adjtree = adjacenttile(point, tree, oldmap) + \
                    adjacenttile(point, water, oldmap)
                if (adjtree > 0 and
                    random.random() < forestsize and
                    oldmap.gettile(i, j) == ground):
                    newmap.settile(point, tree)

    # ruin
    for i in range(1, width-1):
        for j in range(1, height-1):
            if (random.random() < percentruins and
                not newmap.gettile(i, j) == water):
                newmap.settile(tuple([i, j]), ruin)

    for g in range(gens):
        oldmap = newmap.copy()
        for i in range(1, width-1):
            for j in range(1, height-1):
                point = tuple([i, j])
                adjruin = adjacenttile(point, ruin, oldmap)
                if (adjruin > 0 and
                    random.random() < ruinsize and
                    (oldmap.gettile(i, j) == ground or
                     oldmap.gettile(i, j) == wall)):
                    newmap.settile(point, ruin)

    return newmap

def setsemifarstairs(worldmap):
    groundtiles = worldmap.getgroundtiles()
    s1 = random.choice(groundtiles)
    while (adjacenttile(s1, wall, worldmap) > 2):
        s1 = random.choice(groundtiles)
    groundtiles = sorted(groundtiles,
                         key=lambda tile: manhattandist(s1, tile),
                         reverse=True)
    tiles = groundtiles[:]
    s2 = random.choice(tiles)
    while (astar(s1, s2, worldmap) < 20 and
           len(tiles) > 0 and
           (adjacenttile(s2, wall, worldmap)+\
            adjacenttile(s2, water, worldmap)) > 2):
        s2 = random.choice(tiles)
        tiles.remove(s2)
    
    worldmap.setstair(1, s1)
    worldmap.setstair(2, s2)

    return astar(s1, s2, worldmap)

def drawmap(worldmap):
    print('%d : %s, %s' % (astar(worldmap.s1, worldmap.s2, worldmap),
                           worldmap.s1, worldmap.s2))
    for row in range(height):
        print(''.join(worldmap.tiles[row*width:(row+1)*width]))

def main():
    maps = 0
    mapgenerator = cellularautomata

    mindist = sqrt(size) * 0.9
    
    while(1):
        input()
        tilemap = mapgenerator()
        dist = setsemifarstairs(tilemap)

        stairstries = 0
        while dist < mindist:
            if stairstries < 20:
                dist = setsemifarstairs(tilemap)
                stairstries += 1
            else:
                print("making new map...")
                mapgenerator()
                stairstries = 0
            
        drawmap(tilemap)

if __name__=="__main__":
    main()
