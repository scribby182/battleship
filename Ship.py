from Coord import Coord
import copy
from printArgs import printArgs


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
		self.coords = [None for x in range(1,length+1)]
		self.hits = [False,] * self.length

	def __repr__(self, debug = False):
		"""
		# Format the printing of Ships
		# This defines what is returned when I do "print(myShip)", that way I don't need to keep writing something
		# like "print("Ship {} is at {}".format..."
		"""

		# Format coordinate output
		coordsStr = "[" + ", ".join(["{}".format(coord) for coord in self.coords]) + "]"

		# Format self.hits output with same spacing as CoordsStr.  To do this, strip
		# the [], then separate by ", " and take the size of each remaining part
		# to space everything
		# I could have also built this up in a for loop while building coordsStr,
		# but this works and lets me try something more complex...  This really
		# isn't as robust though, especially since I rely on the separator ", "
		tempHitsFormat = coordsStr.lstrip('[(').rstrip(')]').split("), (")
		hitsStr = "["
		for i in range(0,len(tempHitsFormat)):

			# Elements have "), (" between them stripped as well as
			# leading/trailing parentheses.  Need to pad width value
			# Last element needs padding of 2.  Others need 4
			if i == len(tempHitsFormat)-1:
				widthshift = 2
			else:
				widthshift = 4
			width = len(tempHitsFormat[i]) + widthshift
			hitsStr = hitsStr + "{0:<{1}}".format(str(self.hits[i]),width)
		hitsStr = hitsStr + "]"

		return "{shipClass:<12} ({ID}): {name}\nLength          : {length}\nLocation        : {location}\n{hitHeader:<16}: {hits}".format(shipClass=self.shipClass, ID=self.boardID, name=self.name, length=self.length, location=coordsStr, hitHeader="Hits:", hits=hitsStr)


	def placeShip(self,coords):
		"""
		Method for setting the coordinates of a ship.
		:param coords: list of tuples or Coord objects.  Tuples will be converted internally to Coord objects.
		:return: Return 1 if completed (not sure why I did this...)
		"""
		if len(coords) == self.length:
			self.coords = [coord if isinstance(coord,Coord) else Coord(coord) for coord in coords]
		else:
			raise IncorrectShipLength("Ship \"{}\" expects coords of length {}, received length {}".format(self.name, self.length, len(coords)))
		return 1


	def getStraightCoords(self, origin, direction, debug = False):
		"""
		Method to generate the coordinates of a ship based on an origin coordinate and direction (U/D/L/R).

		:param origin: Tuple coordinate for one end of the ship
		:param direction: String (U/D/L/R indicating Up/Down/Left/Right) for the direction to place the ship relative to the origin

		:return:  List of tuples for the coordinates of the ship
		"""

		if debug == True:
			printArgs(exclude=['self'])

		# Initialize the output list
		coords = [None] * self.length

		# Set the first coordinate
		# Convert origin to Coord object if necessary
		if not isinstance(origin, Coord):
			coords[0] = Coord(origin)
		else:
			coords[0]=copy.deepcopy(origin)

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
			# Make a new coord object rather than update
			coords[i] = Coord((coords[i-1].x + deltaCoord[0], coords[i-1].y + deltaCoord[1]))

		return coords



	def takeFire(self, fireCoord, debug=False):
		"""
		Accepts a coordinate being fired on and returns either -1 (miss) or the integer number of the segment that was hit.

		If hit, method updates the ship's record of hits.  If hit somewhere that is already hit, method raises a
		HitDuplicate exception.

		:param fireCoord: Tuple coordinate of fire to test for a hit
		:return: -1 (miss) or integer segment of the ship that was hit (ie: fireCoord == ship.coord[2], return 2)
		"""
		# Convert fireCoord to a Coord object if necessary
		if not isinstance(fireCoord,Coord):
			fireCoord = Coord(fireCoord)
		else:
			fireCoord = copy.deepcopy(fireCoord)

		if debug==True:
			print("Ship {} taking fire at coord {}".format(self.name,fireCoord))
		try:
			coordStatus = self.coordStatus(fireCoord)
			if coordStatus['hit'] == True:
				raise HitDuplicate("Ship {} already hit at coordinate {}".format(self.name, fireCoord))
			else:
				# Assign the hit to the ship
				self.hits[coordStatus["i"]] = True

				# Print to screen for debugging
				if debug==True:
					print("Ship {} hit at coordinate {}".format(self.name, fireCoord))

				# Return the index of the hit
				return(coordStatus["i"])
		# # TODO: Do I need both of these exceptions?
		# except ValueError:
		# 	# Return -1 for a miss
		# 	if debug==True:
		# 		print("Ship {} missed at coordinate {}".format(self.name, fireCoord))
		# 	return(-1)
		except InvalidCoord:
			# Indicates the coord was either not valid or not on the ship at all
			if debug == True:
				print("Ship {} missed at coordinate {}".format(self.name, fireCoord))
			return (-1)

	# Return the health of a ship.  Returned results are:
	#  [hits remaining, hits taken]
	def getHealth(self):
		"""
		Returns a tuple of the health of this ship (hitsRemaining, hitsTaken)

		:return: A tuple of (hitsRemaining, hitsTaken) for this ship
		:return: A dictionary with hits "taken" and hits "remaining"
		"""
		hitsTaken = self.hits.count(True)
		hitsRemaining = self.hits.count(False)
		return {"taken": hitsTaken, "remaining": hitsRemaining}

	def coordStatus(self, coord, debug=False):
		"""
		Accepts a coordinate and returns the status of that coordinate on the ship

		Raises an exception InvalidCoord if the coordinate is not on the ship
		or invalid.

		:param coord: Tuple of row/col coordinate to interrogate
		:return: Dictionary of information about that coordinate on the ship:
			{i: integer index of the position on the ship,
			 hit: Boolean indicating if this position has been hit}
		"""

		# Convert coord to Coord object if necessary
		if not isinstance(coord, Coord):
			coord = Coord(coord)
		else:
			coord = copy.deepcopy(coord)

		if debug == True:
			print("Checking ship {}'s status at coordinate {}".format(self.name, coord))
			printArgs()
			print(type(coord))

		# Find the coord in the ship
		try:
			# Does this work with Coord object?
			i = self.coords.index(coord)
		except ValueError:
			raise InvalidCoord("Coordinate {} is not on ship {}".format(coord,self.name))

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
	# ships.append(HugeShip("Dr. HugeShip"))

	printShips(ships)

	print("")
	print("Placing the ships.")
	# Place the battleship arbitrarily
	coords = [(0,i) for i in range(0,5)]
	ships[0].placeShip(coords)

	# Place the submarine using getStraightCoord
	dir = "R"
	# reverse the order of these just to be fancy
	coords = ships[1].getStraightCoords((0,3),dir)[::-1]
	print(coords)
	ships[1].placeShip(coords)

	printShips(ships)

	# Test coordStatus by probing ships
	coords = [(0,0), (0,3), (0,6), "not valid", (5,'not valid')]
	for coord in coords:
		try:
			print(ships[0].coordStatus(coord))
		except Exception as e:
			print("caught exception: {}".format(e))

	print('Shooting the ships')
	# Fire on the ship
	coords = [(0,0), (0,3), (0,6), "not valid", (5,'not valid')]
	for ship in ships:
		for coord in coords:
			try:
				x = ship.takeFire(coord)
				print("ship.takeFire returned {}".format(x))
				print(ship.coordStatus(coord))
			except Exception as e:
				print("caught exception: {}".format(e))

	for ship in ships:
		print(ship.getHealth())

	printShips(ships)
#
	#

	# # Add ships to board
	# print("Add ships to board:")
	# myBoard.addShip(mySubmarine)
	# myBoard.addShip(myBattleship)
	# #print(myBoard)

