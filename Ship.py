################################################################################
# Ship class
################################################################################
class Ship(object):
	def __init__(self, name, shipClass, boardID, length):
		self.name = name
		self.shipClass = shipClass
		if len(boardID) != 1 and isinstance(boardID, str):
			raise InvalidBoardIDLength("boardID must be single character")
		self.boardID = boardID
		self.length = length

		# Initialize coordinates and hits
		self.coords = [(-1,-1) for x in range(1,length+1)]
		self.hits = [0,] * self.length

	def __repr__(self):
		"""
		# Format the printing of Ships
		# This defines what is returned when I do "print(myShip)", that way I don't need to keep writing something
		# like "print("Ship {} is at {}".format..."
		"""

		# Format coordinate output
		coordsStr = "[" + ", ".join("(%s,%s)" % coord for coord in self.coords) + "]"

		# Format self.hits output with same spacing as CoordsStr.  To do this, strip
		# the [], then separate by ", " and take the size of each remaining part
		# to space everything
		# I could have also built this up in a for loop while building coordsStr,
		# but this works and lets me try something more complex...  This really
		# isn't as robust though, especially since I rely on the separator ", "
		tempHitsFormat = coordsStr.strip("[]").split(", ")
		hitsStr = "[ "
		for i in range(0,len(tempHitsFormat)):
			if i == len(tempHitsFormat)-1:
				widthshift = -1
			else:
				widthshift = 2
			width = len(tempHitsFormat[i]) + widthshift
			hitsStr = hitsStr + "{0:<{1}}".format(self.hits[i],width)
		hitsStr = hitsStr + "]"

		return "{shipClass:<12} ({ID}): {name}\nLength          : {length}\nLocation        : {location}\n{hitHeader:<16}: {hits}".format(shipClass=self.shipClass, ID=self.boardID, name=self.name, length=self.length, location=coordsStr, hitHeader="Hits:", hits=hitsStr)


	def placeShip(self,coords):
		"""
		Method for setting the coordinates of a ship.
		:param coords: list of tuples, one for each segment of a ship.
		:return: Return 1 if completed (not sure why I did this...)
		"""
		if len(coords) == self.length:
			self.coords = coords
		else:
			raise IncorrectShipLength("Ship \"{}\" expects coords of length {}, received length {}".format(self.name, self.length, len(coords)))
		return 1

	# Takes the origin and direction of a straight ship (either constant row
	# or constant column) and computes the ship's coordinates
	def getStraightCoords(self,origin,direction):
		"""
		Method to generate the coordinates of a ship based on an origin coordinate and direction (U/D/L/R).

		:param origin: Tuple coordinate for one end of the ship
		:param direction: String (U/D/L/R indicating Up/Down/Left/Right) for the direction to place the ship relative to the origin

		:return:  List of tuples for the coordinates of the ship
		"""

		# Initialize the output list
		coords = [None] * self.length

		# Set the first coordinate
		coords[0]=origin

		# Assign a position delta based on the direction variable
		deltaCoord = ()
		if direction.upper() == "D":
			deltaCoord = (1,0)
		elif direction.upper() == "U":
			deltaCoord = (-1,0)
		elif direction.upper() == "R":
			deltaCoord = (0,1)
		elif direction.upper() == "L":
			deltaCoord = (0,-1)

		# Assign the rest of the coordinates
		for i in range(1,self.length):
			coords[i] = (coords[i-1][0] + deltaCoord[0], coords[i-1][1] + deltaCoord[1])

		return coords

	# Method determines if ship is hit by fire, logs any hits, and returns results
	# Return values are:
	#	N (>1): the index of the coordinate hit
	#	-1: miss
	#	-2: hit, but the ship was already hit there anyway

	def takeFire(self, fireCoord, debug=False):
		"""
		Accepts a coordinate being fired on and returns either -1 (miss) or the integer number of the segment that was hit.

		If hit, method updates the ship's record of hits.  If hit somewhere that is already hit, method raises a
		HitDuplicate exception.

		:param fireCoord: Tuple coordinate of fire to test for a hit
		:return: -1 (miss) or integer segment of the ship that was hit (ie: fireCoord == ship.coord[2], return 2)
		"""
		if debug==True:
			print("Ship {} taking fire at coord {}".format(self.name,fireCoord))
		try:
			if self.hits[self.coords.index(fireCoord)] == 1:
				raise HitDuplicate("Ship {} already hit at coordinate ({},{})".format(self.name, fireCoord[0],fireCoord[1]))
			else:
				# Get the index of the coordinate taking a hit.  Log a hit at that index
				hitIndex = self.coords.index(fireCoord)
				self.hits[hitIndex] = 1

				# Print to screen for debugging
				if debug==True:
					print("Ship {} hit at coordinate ({},{})".format(self.name, fireCoord[0],fireCoord[1]))

				# Return the index of the hit
				return(hitIndex)
		except ValueError:
			# Return -1 for a miss
			if debug==True:
				print("Ship {} missed at coordinate ({},{})".format(self.name, fireCoord[0],fireCoord[1]))
			return(-1)

	# Return the health of a ship.  Returned results are:
	#  [hits remaining, hits taken]
	def getHealth(self):
		"""
		Returns a tuple of the health of this ship (hitsRemaining, hitsTaken)

		:return: A tuple of (hitsRemaining, hitsTaken) for this ship
		"""
		hitsTaken = self.hits.count(1)
		hitsRemaining = self.hits.count(0)
		return (hitsRemaining, hitsTaken)

	def coordStatus(self,coord):
		"""
		Accepts a coordinate and returns the status of that coordinate on the ship

		Raises an exception InvalidCoord if the coordinate is not on the ship
		or invalid.

		:param coord: Tuple of row/col coordinate to interrogate
		:return: Dictionary of information about that coordinate on the ship:
			{i: integer index of the position on the ship,
			 hit: Boolean indicating if this position has been hit}
		"""

		# Find the coord in the ship
		# TODO: Validate coord (tuple of 2 integers, etc)
		try:
			i = self.coords.index(coord)
		except ValueError:
			raise InvalidCoord("Coordinate ({},{}) is not on ship {}".format(coord[0],coord[1],self.name))

		hit = self.hits[i]

		return {"i": i, "hit": hit}


	###########################
# Ship Subclasses
###########################
class Battleship(Ship):
	"""
	Subclass for a battleship, which has length 5 and is shown as a "B" on the board
	"""
	def __init__(self,name):
		shipClass = "Battleship"
		boardID = "B"
		length = 5
		super().__init__(name, shipClass, boardID, length)

class Submarine(Ship):
	"""
	Subclass for a submarine, which has length 3 and is shown as a "S" on the board
	"""
	def __init__(self,name):
		shipClass = "Submarine"
		boardID = "S"
		length = 3
#		coords = self.straightShipCoords(origin,direction)
		super().__init__(name, shipClass, boardID, length)

class HugeShip(Ship):
	"""
	Subclass for a hugeship (for debugging), which has length 30 and is shown as a "!" on the board
	"""
	def __init__(self,name):
		boardID = "!"
		shipClass = "Huge Ship"
		length = 30
		super().__init__(name, shipClass, boardID, length)


###########################
# Exceptions
###########################
class IncorrectShipLength(Exception):
	def __init__(self,value):
		self.value = value
	def __str__(self):
		return repr(self.value)

# Exception for when a board/ship takes a redundant hit
class HitDuplicate(Exception):
	def __init__(self,value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class InvalidBoardIDLength(Exception):
	def __init__(self,value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class InvalidCoord(Exception):
	"""
	Class for raising error when interrogating a ship about a coordinate that is
	invalid (not on ship, non-numeric/integer, etc.)
	"""
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)


###########################
# Test code for the methods
###########################
if __name__ == '__main__':
	# Show off all your fancy methods!

	###############
	# DEBUG: Make ships
	###############

	# For printing a list of ships
	def printShips(ships):
		print("Ships look like:")
		for ship in ships:
			print(ship)

	print("Making some ships.")
	ships = []

	# Initialize some ships
	ships.append(Battleship("Mr. Battleship"))
	ships.append(Submarine("Mrs. Submarine"))
	ships.append(HugeShip("Dr. HugeShip"))

	printShips(ships)

	print("")
	print("Placing the ships.")
	# Place the battleship arbitrarily
	coords = [(0,i) for i in range(0,5)]
	ships[0].placeShip(coords)

	# Place the submarine using getStraightCoord
	dir = "R"
	coords = ships[1].getStraightCoords((1,0),dir)
	ships[1].placeShip(coords)

	printShips(ships)


	# # Add ships to board
	# print("Add ships to board:")
	# myBoard.addShip(mySubmarine)
	# myBoard.addShip(myBattleship)
	# #print(myBoard)

