import sys
import copy
from Ship import Ship
from Ship import Battleship


# To color text on the board
from colorama import init, Fore, Style
init()


################################################################################
# Board class
################################################################################
class Board(object):
	"""
	Object that saves the placement of a player's ships and includes methods to interact with those ships
	"""

	# NOTE: I want to initialize some variables in all board classes. Initially,
	# I did this with the following code (which defines two class variables):
	#   ships = []
	#   waterhits = []
	# This is VERY wrong for two reasons:
	# 1)	I just want default values - why use class variables?  Class variables
	#		apply across the whole class, ie the entire class shares the SAME variable,
	#       not that they all have a similar slot for their own data.
	# 2)	In this case, I've also made MUTABLE objects, so if I do:
	#			board1 = Board(...)
	#			board2 = Board(...)
	#			board1.ships.append("something")
	#			print(board2.ships)
	#				-->result: "something"
	#		This is because mutable class objects are not masked, they're changed
	#		in place.  Thus, they're always going to be linked.
	#       I'm not sure what would happen if the append was replaced with an
	#       assignment (never checked), but either way it isn't doing what I
	#       intended here.
	# What I really want is to put these inside __init__, and I also want to
	# be careful how I define their defaults because:
	# 	def function(data=[]):
	#		data.append(1)
	#		return data
	#	print(function) --> result: [1]
	#	print(function) --> result: [1,1]
	# because default variables are evaluated when, and only when, the def
	# command is evaluated.  Thus, a single mutable list ([]) is generated for
	# all calls to the function and just changed over and over again in future.

	def __init__(self, rows, cols, name="Unnamed"):
		self.name = name
		self.rows = rows
		self.cols = cols

		# Initialize storage containers for ships and hits to water
		self.ships = []
		self.waterhits = []

		# shipMap is the internal representation of the ships on the board,
		# where -1 means nothing and any value of >=0 is the index of the ship
		# in the self.ships container (ie, if shipMap[1][2] = 5, that square is
		# occupied by the ship ships[5].name)
		#
		# NOTE: I first tried to initialize like this:
		#   self.shipMap = [[-1]*cols]*rows
		# but because the [-1]*cols makes a mutable object, the *rows just makes
		# a bunch of references to the same initial mutable object.  That means
		# changing element 0,0 also changes elements 1,0, 2,0, ...
		self.shipMap = [[-1 for x in range(cols)] for x in range(rows)]

		# NOTE: I don't think I ended up fully using the shipMap.  I ended up
		# building the map during display() calls, and only using it during
		# addship... could probably remove it with little effort.  Or used more below to
		# actually take advantage of the thing...



	def display(self, boardView, shipView):
		"""
		Method to generate a string showing the status of the board.

		Board squares and ship identities can be obscured depending on mode selected.
		For all modes, color coding is as follows:
			Water = Bright blue (not hit) or dim blue (hit)
			Ships = Yellow (not hit) or red (hit)

		NOTE: I think this can be refactored to simplify greatly, but haven't tried yet.

		:param boardView: Toggle for board viewing modes:
							0 - show the entire board, including all ships (god mode)
							1 - show the board revealed so far (only where shots fired)
		:param shipView: Toggle for the ship viewing modes:
							0- show ships as their index
							1- show ships as their ID character
		:return:
		"""

#		TODO: display method needs SERIOUS overhaul

		# Define the size of the border regions (must be big enough for all
		# header/sider digits, plus a spacer character)
		# 	floor(number of row/col / 10) + 1 for first digit + 1 for spacer
		border = {'header': self.cols // 10 + 2, 'sider': self.rows // 10 + 2}

		# character used for any unexplored region of the board
		charUnknown = "?"

		# Character for square with hit on unknown ship
		charUnknownHit = Fore.RED + "?" + Style.RESET_ALL

		# Define border text style as function (easier to update later)
		def borderText(text):
			return Fore.CYAN + str(text) + Style.RESET_ALL

		# Define spacer characters
		headerSpacer = "-"
		siderSpacer = "|"

		# Initialize list representation of board (makes it easier to build in
		# pieces)
		boardLst = [[charUnknown.lower() for x in range(1, self.cols + 1 + border['sider'])] for x in
		            range(1, self.rows + 1 + border['header'])]

		# Set header
		for x in range(1, self.cols + 1):
			# Save x as a right justified string with whitespace to the left.
			# This gives an easy way to fill in the header region
			# Probably could have done this straight in the for loop call...
			xAsStr = "{x: >{width}}".format(x=x, width=border['header'] - 1)

			# For each row of the header, fill in the appropriate character from
			# x.  First row gets left most character, next row gets second left
			# most, etc...
			for y in range(1, border['header']):
				#				boardLst[y-1][border['sider']+x-1] = borderStyle + xAsStr[y-1] + Style.RESET_ALL
				boardLst[y - 1][border['sider'] + x - 1] = borderText(xAsStr[y - 1])
			# Set the header spacer line
			boardLst[border['header'] - 1][border['sider'] + x - 1] = borderText(headerSpacer)

		for x in range(1, self.rows + 1):
			# Same comments as above...
			xAsStr = "{x: >{width}}".format(x=x, width=border['sider'] - 1)
			for y in range(1, border['sider']):
				boardLst[border['header'] + x - 1][y - 1] = borderText(xAsStr[y - 1])
			boardLst[border['header'] + x - 1][border['sider'] - 1] = borderText(siderSpacer)

		# Change top left corner between borders to whitespace
		for row in range(0, border['header']):
			for col in range(0, border['sider']):
				boardLst[row][col] = " "

		# Add ships to board
		# Loop through all ships on board
		for i, ship in enumerate(self.ships):
			# Define display formats:
			# charShip[0] is for tiles yet to be hit, [1] for tiles hit
			# Update: ship.coords loop below now bypasses charShip when
			# boardview==0 and ship is not sunk (ship identity shouldn't be
			# available if ship is only partially hit).  There's probably a
			# better way to do this, but I didn't bother...
			charShip = ["", ""]
			if boardView == 0:
				if shipView == 0:
					charShip[0] = Fore.YELLOW + str(i) + Style.RESET_ALL
					charShip[1] = Fore.RED + str(i) + Style.RESET_ALL
				elif shipView == 1:
					charShip[0] = Fore.YELLOW + ship.boardID + Style.RESET_ALL
					charShip[1] = Fore.RED + ship.boardID + Style.RESET_ALL
			elif boardView == 1:
				if shipView == 0:
					charShip[0] = charUnknown
					charShip[1] = Fore.RED + str(i) + Style.RESET_ALL
				elif shipView == 1:
					charShip[0] = charUnknown
					charShip[1] = Fore.RED + ship.boardID + Style.RESET_ALL

			# For all ship hits, update the board.  If:
			# 	boardView==0 : show the ship ID char or ID number
			#	boardView==1 && ship=sunk:  show the ship ID char or ID number
			#	else: show  charUnknownHit
			# Loop through ships coordinates
			for j, coord in enumerate(ship.coords):
				# If this coordinate was hit, update tile
				if ship.hits[j] == 1:
					if boardView == 0 or (boardView == 1 and ship.getHealth()[0] == 0):
						boardLst[coord[0] - 1 + border['header']][coord[1] - 1 + border['sider']] = charShip[
							ship.hits[j]]
					else:
						boardLst[coord[0] - 1 + border['header']][coord[1] - 1 + border['sider']] = charUnknownHit

		# Add water hits to board
		charWaterHit = Fore.BLUE + "X" + Style.RESET_ALL
		for coord in self.waterhits:
			boardLst[coord[0] - 1 + border['header']][coord[1] - 1 + border['sider']] = charWaterHit

		# Assemble boardLst into string for output
		# Update adding board's name to output at the start of the print:
		# boardStr = ""
		boardStr = "Board: " + self.name + "\n"
		for row in boardLst:
			boardStr = boardStr + ("".join(row)) + "\n"

		return boardStr

	def __repr__(self):
		"""
		Print using custom display method with boardView = 0 and shipView = 0 (god mode)

		:return: String showing the state of the board
		"""

		# Use display method to create god-mode output using ship indices
		return self.display(0, 0)

	# getHealth, for a given board, returns:
	#   [hitsRemaining, hitsTaken] where:
	#	hitsRemaining is the sum of hits remaining for all ships on the board
	#	hitsTaken is the sum of hits taken by all the ships on the board
	def getHealth(self):
		"""
		Returns for this board the sum of the hits remaining for all ships and the hits taken by all ships as a list.

		:return: [hitsRemaining, hitsTaken], where:
					hitsRemaining is the sum of hits remaining for all ships on this board
					hitsTaken is the sum of hits taken by all ships on this board
		"""
		hitsRemaining = 0
		hitsTaken = 0

		for ship in self.ships:
			[tempHitsRemaining, tempHitsTaken] = ship.getHealth()
			hitsRemaining = hitsRemaining + tempHitsRemaining
			hitsTaken = hitsTaken + tempHitsTaken

		return [hitsRemaining, hitsTaken]

	# addShip method accepts an existing ship class and adds it to the board.
	# The method also checks to make sure the ship is on the board and does not
	# does not overlap with any existing ships
	def addShip(self, ship, debug=False):
		"""
		Accepts a Ship object and adds it to the board, checking whether ship placement is valid (on board, no overlap)

		If ship placement is not valid, an exception will be raised.

		:param ship: A Ship object with coordinates defined
		:return: Nothing, but updates .shipmap and .ships
		"""
		# Check inputs for correctness (ship must be a Ship object)
		if (not isinstance(ship, Ship)):
			raise InvalidShip("Invalid input to addShip - must be Ship class")

		# Check ship for valid position (fully on map, not on other ships, etc.)
		# Loop through each position to check validity.  Store local copy of
		# shipMap, then update this local copy with each coordinate as you
		# test them.  If all coordinates are valid, set shipMap=tempShipMap
		#
		# This way we don't loop through the coords twice (one to test, one to set)!

		# Make a deepcopy of shipMap to work on locally (need deepcopy because
		# shipMap is a mutable object of mutable objects
		tempShipMap = copy.deepcopy(self.shipMap)

		# Determine next available ship index.  Store for use
		nextShipIndex = len(self.ships)

		# Loop through ship's coordinates, checking if they're valid/free
		# and if so placing the ship on them.
		# This gets complicated because ship.coords are in a 0 index system,
		# but the board was stored in a 1 index system.  Need to make this
		# easier...
		for coord in ship.coords:
			if debug == True:
				print("Trying to place ship {} at coord ({},{})".format(ship.name, coord[0], coord[1]))
			# Check if row is inside board
			if (coord[0] - 1 < 0 or coord[0] - 1 > self.rows):
				raise InvalidShip("New ship {0} must be within board ( 1 <= row <= {1}".format(ship.name, self.rows))
			# Check if col is inside board
			elif (coord[1] - 1 < 0 or coord[1] - 1 > self.cols):
				raise InvalidShip("New ship {0} must be within board ( 1 <= col <= {1}".format(ship.name, self.cols))
			# Check if coordinate is already taken
			elif tempShipMap[coord[0] - 1][coord[1] - 1] >= 0:
				overlapShipNum = tempShipMap[coord[0] - 1][coord[1] - 1]
				overlapShipName = self.ships[overlapShipNum].name
				raise InvalidShip("New ship {0} overlaps previous ship {1} (ID: {2})".format(ship.name, overlapShipName,
				                                                                           overlapShipNum))
			# If nothing went wrong, place this pip of the ship.
			else:
				if debug == True:
					print("\tPassed all checks - ship fits!")
					print("\tupdating coord ({},{})".format(coord[0] - 1,
					                                        coord[1] - 1))
					print("\tshipMap was {}".format(tempShipMap[coord[0] - 1][coord[1] - 1]))
				tempShipMap[coord[0] - 1][coord[1] - 1] = nextShipIndex
				if debug == True:
					print("\tshipMap now {}".format(
									tempShipMap[coord[0] - 1][coord[1] - 1]))

		# If we get here, all coordinates worked.  Add ship to .ships and
		# move the local copy of shipMap (tempShipMap) back to the big time
		self.ships.append(ship)
		# TODO: Can't this just be self.shipMap = tempShipMap ?  Then I don't make an extra copy and delete the existing tempShipMap.
		self.shipMap = copy.deepcopy(tempShipMap)

	def takeFire(self, fireCoord, debug=False):
		"""
		Accepts a tuple coordinate that is being shot at, determines if there is a ship at that coordinate, and updates the ship/water hits accordingly.

		Return values are:
		-	N (>1): index of the ship hit
		-	-1: indicates a miss
		-	-2: indicates a repeated shot (water or ship hit)

		Exceptions are raised if
		-   FireOutsideBoard - fireCoord is not within the board
		-   FireRedundant - fireCoord is a redundant shot (board already hit there)

		:param fireCoord: Tuple coordinate to attempt to hit
		:return:  See above
		"""

		# Algorithm:
		#	-	Check if fire is within board.  Raise error if it isn't.
		#	-	Loop through ships and check if any are hit.
		#		-	If hit is new, return index
		#		-	If hit is a repeat, raise an exception
		#	-	Check water to find repeat shot
		#		-	If shot is new, return -1
		#		-	If shot is a repeat, raise an exception

		if debug == True:
			print("Board {} taking fire at coord {}".format(self.name, fireCoord))

		# Check if fireCoord is within board
		if (fireCoord[0] > self.rows or fireCoord[0] < 1 or fireCoord[1] > self.cols or fireCoord[1] < 1):
			message = "({},{}) is outside board ({} rows, {} cols)".format(fireCoord[0], fireCoord[1], self.rows,
			                                                               self.cols)
			raise FireOutsideBoard(message)
		hitany = -1

		# Loop through ships to see if any are hit
		for i, ship in enumerate(self.ships):
			try:
				# ship.takeFire returns the ship's index that was hit if a hit,
				# otherwise it returns -1 for a miss or an exception if this shot
				# is redundant
				hitthis = ship.takeFire(fireCoord)
			# If ship has already been hit here, raise exception
			except FireRedundant:
				raise FireRedundant("Board hit with redundant shot on ship {} ({})".format(ship.name, i))

			# Record the ship that was hit
			if hitthis >= 0:
				hitany = i
				break

		# No ship hit - check water to see if it is new or redundant and act
		# accordingly
		if hitany == -1:
			if fireCoord in self.waterhits:
				raise FireRedundant("Board hit with redundant shot in water")
			else:
				self.waterhits.append(fireCoord)

		return hitany

	###########################
	# Properties
	###########################
	# Used for easier error checking on values for rows/cols
	@property
	def rows(self):
		# Not sure what this "doc" docstring does.  Maybe I'll find out by trying?
		#		"""I'm the rows property""" # For some reason this breaks the next line in the code...
		return self._rows

	@rows.setter
	def rows(self, value):
		valueMin = 5
		if not value > valueMin:
			raise NotEnoughRows("Must have more than {} rows".format(valueMin))
		self._rows = value

	@property
	def cols(self):
		# Not sure what this "doc" docstring does.  Maybe I'll find out by trying?
		#		"""I'm the rows property""" # For some reason this breaks the next line in the code...
		return self._cols

	@cols.setter
	def cols(self, value):
		valueMin = 5
		if not value > valueMin:
			raise NotEnoughRows("Must have more than {} cols".format(valueMin))
		self._cols = value


###########################
# Exceptions
###########################
class InvalidShip(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

class NotEnoughRows(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

# This second one really isn't necessary.. could just be NotEnoughRowsCols or
# something and share...
class NotEnoughCols(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

# Exception for when shooting outside board
class FireOutsideBoard(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

# Exception for when a board/ship takes a redundant hit
class FireRedundant(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

###########################
# Test code for the methods
###########################
if __name__ == '__main__':
	# Show off all your fancy methods!

	###########################
	# Make some boards
	###########################
	print("Make an 8x8 board:")
	try:
		myBoard = Board(8,8)
	except NotEnoughRows as e:
		print("Caught exception: " + str(e))
		sys.exit(1) #just some error code
	except NotEnoughCols as e:
		print("Caught exception: " + str(e))
		sys.exit(1) #just some error code

	print(myBoard)
	print()

	print("Make a 15x12 board with a name:")
	try:
		myBoard2 = Board(15,12, name="Andrew")
	except NotEnoughRows as e:
		print("Caught exception: " + str(e))
		sys.exit(1) #just some error code
	except NotEnoughCols as e:
		print("Caught exception: " + str(e))
		sys.exit(1) #just some error code

	print(myBoard2)
	print()

	print("Make a 4x6 board")
	try:
		myBoard3 = Board(4,6)
	except NotEnoughRows as e:
		print("Caught exception: " + str(e))
	except NotEnoughCols as e:
		print("Caught exception: " + str(e))

	try:
		print(myBoard3)
	except Exception as e:
		print("Can't print myBoard3")


	###########################
	# Place ships on the boards
	###########################
	# Make some ships
	print("Make some ships:")
	bShip1 = Battleship("Battleship1")
	coords = [(2,i) for i in range(1,bShip1.length+1)]
	bShip1.placeShip(coords)
	print(bShip1)
	bShip2 = Battleship("Battleship1")
	coords = [(3,i) for i in range(1,bShip2.length+1)]
	bShip2.placeShip(coords)
	print(bShip2)

	# Add ships to board
	print("Add ships to board:")
	myBoard.addShip(bShip1,debug=True)
	myBoard.addShip(bShip2,debug=True)
	print("Print the board with god-mode vision")
	print(myBoard.display(0,0))
	print(myBoard.shipMap)
	# print(myBoard.display(1,0))
	# print(myBoard.display(0,1))
	# print(myBoard.display(1,1))


	# # Initialize some ships
	# ships.append(Battleship("Mr. Battleship"))
	# ships.append(Submarine("Mrs. Submarine"))
	# ships.append(HugeShip("Dr. HugeShip"))
	#
	# printShips(ships)
	#
	# print("")
	# print("Placing the ships.")
	# # Place the battleship arbitrarily
	# coords = [(0,i) for i in range(0,5)]
	# ships[0].placeShip(coords)
	#
	# # Place the submarine using getStraightCoord
	# dir = "R"
	# coords = ships[1].getStraightCoords((1,0),dir)
	# ships[1].placeShip(coords)