import ai as AI

class Entity:
	def __init__(self, x, y, char, name,
		description=None, blocks=False, fighter=None, ai=None, door=None):

		self.x = x
		self.y = y
		self.char = char
		self.name = name
		self.blocks = blocks
		self.fighter = fighter
		self.ai = ai
		self.door = door

		if self.fighter:
			self.fighter.owner = self

		if self.ai:
			self.ai.owner = self

		if self.door:
			self.door.owner = self

		# default description to name
		if description is None:
			description = name
		self.description = description

	def move(self, dx, dy):
		self.x += dx
		self.y += dy

	def move_towards(self, game_map, entities, target, recalc=False):
		if (self.ai.path is False or recalc):
			assert(not target is None)
			self.ai.path = AI.astar((self.x, self.y), 
				(target[0], target[1]), game_map, travonly=True)

		if (self.ai.path): 
			if (len(self.ai.path) > 0):
				x, y = self.ai.path[0]
				if not (game_map.tileblocked(x, y)):
					if (get_blocking_entities_at_location(entities, x, y)):
						# entity in the way! Move around it.
						newmoves = AI.vectorsbyclosestangle(
							(x, y), AI.possible_moves)
						for move in newmoves:
							if not (game_map.tileblocked(x, y) or 
								get_blocking_entities_at_location(entities, x, y)):
								self.move(x-self.x, y-self.y)
								self.ai.path = AI.astar((self.x, self.y), 
									(target[0], target[1]), game_map, travonly=True)
								return True
					else:
						self.move(x-self.x, y-self.y)
						self.ai.path.pop(0)
						return True
			else:
				self.ai.path = False
		return False


def get_blocking_entities_at_location(entities, dest_x, dest_y):
	for entity in entities:
		if entity.blocks and entity.x == dest_x and entity.y == dest_y:
			return entity
	return None
