import dataloader

class MapObjType():
	def __init__(self, name, width, height):
		self.name = name
		self.width = width
		self.height = height
		# sprite

	def print(self):
		result = "%s (width: %d, height %d)" % \
			(self.name, self.width, self.height)
		return result

mapobjdata = dataloader.getdata("mapobj")
# maybe only load the sprite data, etc, if absolutely needed?
mapobjtypes = {}
for key in mapobjdata:
	data = mapobjdata[key]
	mapobjtypes[key] = MapObjType(
		data["name"], data["width"], data["height"])

class MapObject():
	def __init__(self, name, x, y):
		self.position = (x, y)
		self.mapobjtype = mapobjtypes[name]

	def width(self):
		return self.mapobjtype.width

	def height(self):
		return self.mapobjtype.height

	def rect(self):
		result = (
			self.position[0], self.position[1],
			self.mapobjtype.width, self.mapobjtype.height)
		return result

	def collide(self, x, y):
		return collide(x, y, self.rect())

def collide(x, y, rect):
	result = (
		x >= rect[0] and
		x < rect[0] + rect[2] and
		y >= rect[1] and
		y < rect[1] + rect[3])
	return result

def collide_rect(rec1, rect2, buffer=1):
	combined_rect = (
		rect1[0]-(rect2[2]+buffer),
		rect1[1]-(rect2[3]+buffer),
		rect1[2]+(rect2[2]+buffer*2),
		rect1[3]+(rect2[3]+buffer*2))
	result = self.collide(rect2[0], rect2[1], combrect)
	return result