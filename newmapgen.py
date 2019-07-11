import random
from math import sqrt

class Tile:
    def __init__(self, name, blocked, block_sight=None):
        self.name = name
        self.blocked = blocked
        
        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight


wall = Tile('wall', True)
ground = Tile('ground', False)
water = Tile('water', True, False)
exit = Tile('exit', False)
tree = Tile('tree', False, True)

class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.size = width * height
        self.tiles = self.initialize_tiles()

        self.exits = {}
        self.exits['top'] = None
        self.exits['bottom'] = None
        self.exits['left'] = None
        self.exits['right'] = None

    def initialize_tiles(self):
        tiles = [Tile('wall', True) for tile in range(self.size)]
        return tiles

    def tileblocked(self, x, y):
        if self.tiles[x + self.width * y].blocked:
            return True
        return False

    def tilename(self, x, y):
        return self.tiles[x + self.width * y].name

    def copy(self):
        newmap = GameMap(self.width, self.height)
        for i in range(self.size):
            newmap.tiles[i] = self.tiles[i]
        newmap.exits = self.exits
        return newmap

    def settile(self, point, tile):
        self.tiles[point[1] * self.width + point[0]] = tile

    def getgroundtiles(self):
        result = []
        for i in range(self.width):
            for j in range(self.height):
                point = tuple([i, j])
                if (self.tilename(*point) == ground.name):
                    result.append(point)
        # order: top to bottom -> left to right
        return result

    def setexit(self, dir, point):
        assert(dir in self.exits), "map exit direction does not exist"
        if (self.exits[dir] != None and self.tilename(*self.exits[dir]) == exit.name):
            self.settile(self.exits[dir], ground)
        self.exits[dir] = point
        self.settile(point, exit)

    def generate(self):
        self.tiles = self.cellularautomata().tiles
        self.setexits(top = True, bottom = False, left = False, right = False)

    def inbounds(self, x, y, buffer=0):
        return (x < self.width - buffer and
                x >= buffer and
                y < self.height - buffer and
                y >= buffer)

    def adjacenttile(self, point, tiletype, buffer=0):
        result = []
        x = point[0]
        y = point[1]

        if (self.inbounds(x-1, y, buffer) and
            self.tilename(x-1, y) == tiletype.name):
            result.append(tuple([x-1, y]))
        if (self.inbounds(x+1, y, buffer) and
            self.tilename(x+1, y) == tiletype.name):
            result.append(tuple([x+1, y]))
            
        if (self.inbounds(x, y-1, buffer) and
            self.tilename(x, y-1) == tiletype.name):
            result.append(tuple([x, y-1]))
        if (self.inbounds(x, y+1, buffer) and
            self.tilename(x, y+1) == tiletype.name):
            result.append(tuple([x, y+1]))
            
        if (self.inbounds(x-1, y-1, buffer) and
            self.tilename(x-1, y-1) == tiletype.name):
            result.append(tuple([x-1, y-1]))
        if (self.inbounds(x-1, y+1, buffer) and
            self.tilename(x-1, y+1) == tiletype.name):
            result.append(tuple([x-1, y+1]))
        if (self.inbounds(x+1, y-1, buffer) and
            self.tilename(x+1, y-1) == tiletype.name):
            result.append(tuple([x+1, y-1]))
        if (self.inbounds(x+1, y+1, buffer) and
            self.tilename(x+1, y+1) == tiletype.name):
            result.append(tuple([x+1, y+1]))

        return len(result)

    def checkexit(self, exit):
        groundtiles = self.getgroundtiles()
        randomsample = random.sample(groundtiles, int(self.size/40))
        numreached = 0
        total = len(randomsample)
        for tile in randomsample:
            if (astar(exit, tile, self) > 0):
                numreached += 1
        if (numreached >= int(self.height)):
            return True
        else:
            return False

    def setexits(self, top=False, left=True, right=True, bottom=False):
        # get ground tiles
        groundtiles = self.getgroundtiles()

        # top/left front of list, right/bottom back of list
        topleftground = groundtiles[:int(self.height * 3)]
        botrightground = groundtiles[-1*int(self.height * 3):]

        # draw line in direction to edge with ground tiles
        # check to make sure the exits reach most of the randomsample spots
        if top:
            start = random.choice(topleftground)
            mapexit = (start[0], 0)
            while(not self.checkexit(mapexit)):
                start = random.choice(topleftground)
                mapexit = (start[0], 0)
            pathtoexit = [(start[0], start[1]-i) for i in range(0, start[1])]
            for tile in pathtoexit:
                self.settile(tile, ground)
            self.setexit('top', mapexit)
        if left:
            pass
        if right:
            pass
        if bottom:
            pass
        
        
    def cellularautomata(self):
        newmap = GameMap(self.width, self.height)

        scalemod = self.size / 8000 

        percentwalls=.34
        percentwalls += 0.04 * sqrt(scalemod)
        wallsize=0.9
        
        percentwater=.006
        lakesize=0.7
        
        percenttrees=.009
        forestsize=0.62
        
        gens = 3

        # walls
        for i in range(1, self.width-1):
            for j in range(1, self.height-1):
                newmap.settile(tuple([i, j]), ground)
                if ((j == self.height / 2 and
                     random.random() < percentwalls * 1.5) or
                    random.random() < percentwalls):
                    newmap.settile(tuple([i, j]), wall)

        for g in range(gens):
            oldmap = newmap.copy()
            for i in range(1, self.width-1):
                for j in range(1, self.height-1):
                    point = tuple([i, j])
                    adjwalls = oldmap.adjacenttile(point, wall)
                    if (adjwalls >= 4 and
                        random.random() < wallsize):
                        newmap.settile(point, wall)
                    else:
                        newmap.settile(point, ground)

        # water
        for i in range(1, self.width-1):
            for j in range(1, self.height-1):
                if (random.random() < percentwater and
                    newmap.tilename(i, j) == wall.name):
                    newmap.settile(tuple([i, j]), water)

        for g in range(gens):
            oldmap = newmap.copy()
            for i in range(1, self.width-1):
                for j in range(1, self.height-1):
                    point = tuple([i, j])
                    adjwater = oldmap.adjacenttile(point, water)
                    if (adjwater > 0 and
                        random.random() < lakesize and
                        not oldmap.tilename(i, j) == ground.name):
                        newmap.settile(point, water)

        # trees
        for i in range(1, self.width-1):
            for j in range(1, self.height-1):
                if (random.random() < percenttrees and
                    newmap.tilename(i, j) == ground.name):
                    newmap.settile(tuple([i, j]), tree)

        for g in range(gens):
            oldmap = newmap.copy()
            for i in range(1, self.width-1):
                for j in range(1, self.height-1):
                    point = tuple([i, j])
                    adjtree = oldmap.adjacenttile(point, tree) + \
                        oldmap.adjacenttile(point, water)
                    if (adjtree > 0 and
                        random.random() < forestsize and
                        oldmap.tilename(i, j) == ground.name):
                        newmap.settile(point, tree)

        return newmap


############################################################################
######## Extra Stuff for Standalone Testing ################################
############################################################################
movecost = {}
movecost['ground'] = 1
movecost['exit'] = 1
movecost['tree'] = 2
movecost['water'] = 5

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
        if (not travonly or not worldmap.tileblocked(x-1, y)):
            result.append(tuple([x-1, y]))
    if (x + 1 < worldmap.width - buffer):
        if (not travonly or not worldmap.tileblocked(x+1, y)):
            result.append(tuple([x+1, y]))
    if (y - 1 >= buffer):
        if (not travonly or not worldmap.tileblocked(x, y-1)):
            result.append(tuple([x, y-1]))
    if (y + 1 < worldmap.height - buffer):
        if (not travonly or not worldmap.tileblocked(x, y+1)):
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
                gScore[n] = worldmap.size * 10
            t_gScore = gScore[current] + movecost[worldmap.tilename(*n)]
            if n not in openset:
                openset.append(n)
            elif t_gScore >= gScore[n]:
                continue
            camefrom[n] = current
            gScore[n] = t_gScore
            fScore[n] = t_gScore + h(n, goal)
    return -1


def drawmap(gamemap):
    render = {}
    render['wall'] = '#'
    render['ground'] = '.'
    render['water'] = '~'
    render['exit'] = '>'
    render['tree'] = 'F'
    
    for exit in gamemap.exits:
        if exit != (0, 0):
            print('%s: %s' % (exit, gamemap.exits[exit]))
    for row in range(gamemap.height):
        tiles = gamemap.tiles[row*gamemap.width:(row+1)*gamemap.width]
        rendertiles = [render[tile.name] for tile in tiles]
        print(''.join(rendertiles))

def main():
    #width = 230; height = 58 # o lawd he comin
    #width = 180; height = 42 # big boi
    #width = 70; height = 35 # normal size
    #width = 28; height = 16 # mini map
                 
    gamemap = GameMap(70, 35)
    
    while(1):
        input()
        gamemap.generate()   
        drawmap(gamemap)

if __name__=="__main__":
    main()
