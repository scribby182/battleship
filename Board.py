import sys
import copy
from Ship import Ship
from Ship import Battleship
from lst2str import lst2str
from printArgs import printArgs

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



	def display(self, visible="revealed", sDisp="ID" , debug = True):
		"""
		Method to generate a string showing the status of the board.

		Two visibility modes are available:
			all -   Shows all ship locations
					Ships are yellow (not hit) or red (hit)
					Water is dim blue (not hit) or bright blue (hit)
			revealed -  Shows only locations revealed by fire
						Revealed (hit) ships are red
						Revealed (hit) water is bright blue
						Areas not yet revealed are charUnknown

		Two modes are available for displaying fully revealed ship identities:
			ID  -   Ship is identified with its numeric ID
			type-   Ship is identified with its type
		Ship identities are only shown when the ship is fully revealed (ie: if
		visible="all" or visible="revealed" and the ship is destroyed.)


		:param visible: Toggle for board visibility modes:
			all -   Shows all ship locations.
			revealed -  Shows only locations revealed by fire.
		:param sDisp: Toggle for the ship display mode:
			ID  -   Ship is identified with its numeric ID
			type-   Ship is identified with its type
		:return: String shownig the board
		"""

		# Method:
		# Build 2D list of characters for the playing field of the board
		#   For each element of each ship, assign a character to the
		#   corresponding element of the board list.  Choose which type of
		#   character to use based on visible/sDisp
		# Build the header and sider character 2D lists
		# Assemble the lists into a single board
		# Return board as a string

		if debug == True:
			# Print all function arguments to screen for easy debugging
			# Exclude 'self' to avoid infinite loop (printing self calls
			# __repr__, which calls display, which ...
			printArgs(exclude=['self'])

		# Define a character for water that has not been hit
		if visible=="all":
			charWater = "o"
		else:
			charWater = Style.DIM + "o"
		charWater = Fore.BLUE + charWater + Style.RESET_ALL

		# Initialize ocean, a list for the part of the board where sea/ships
		# are located
		ocean = [[charWater for x in range(self.cols)] for y in range(self.rows)]

		# Loop through ships and display them in ocean if appropriate
		for j,ship in enumerate(self.ships):
			if debug == True:
				print("Placing ship \"{}\" in ocean".format(ship.name))

			for i,coord in enumerate(ship.coords):
				if debug == True:
					print("\tProcessing coordinate {} ({},{})".format(i,coord[0],coord[1]))

				# Set character to use for ship based on sDisp
				if sDisp == "ID":
					shipChar = j
				elif sDisp == "type":
					shipChar = ship.boardID
				else:
					raise Exception("Unknown value for sDisp.  Must be \"ID\" or \"type\"")

				# Assign new character to ocean depending on visibility mode
				# and whether the location has been hit
				if visible == "all":
					if ship.hits[i] == True:
						shipChar = Fore.RED + shipChar + Style.RESET_ALL
					else:
						shipChar = Fore.YELLOW + shipChar + Style.RESET_ALL
				elif visible == "revealed":
					if ship.hits[i] == True:
						if ship.getHealth["remaining"] == 0:
							shipChar = Fore.RED + shipChar + Style.RESET_ALL
						else:
							shipChar = Fore.RED + "?" + Style.RESET_ALL
					else:
						# If not hit and visible="revealed", then do not assign anything
						continue
				else:
					raise Exception("Unknown value for visible.  Must be \"all\" or \"revealed\"")

				if debug == True:
					print("\tSea at ({},{}) updated to {}".format(coord[0],coord[1],shipChar))

		# Loop through all water hits and add to board
		charWaterHit = Fore.BLUE + "X" + Style.RESET_ALL
		for coord in self.waterhits:
			ocean[coord[0]][coord[1]] = charWaterHit

		if debug == True:
			print("ocean as string:")
			print(lst2str(ocean))

		# Define the border areas (header and sider)

		# Define border text style as function (easier to update later)
		# Should I have used this above for the ship characters?
		def borderText(text):
			return Fore.CYAN + str(text) + Style.RESET_ALL

		# Generate header and sider
		headerLst = makeHeader(range(self.cols), spacer='-')
		if debug == True:
			print("header as string:")
			print(borderText(lst2str(headerLst)))

		sider = makeHeader(range(self.rows), spacer='|')
		sider = lstTranspose(sider)
		if debug == True:
			print("sider as string:")
			print(borderText(lst2str(sider)))

		# Assemble sider and ocean together
		boardLst = [siderLst[i] + ocean[i] for i in range(len(siderLst))]

		# Top with header, but shift header over by width of sider to align properly
		boardLst = [[" "]*len(siderLst[0]) + row for row in headerLst] + boardLst

		if debug == True:
			print("final board as string:")
			print(lst2str(boardLst))

		return lst2str(boardLst)

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

		if debug == True:
			print("Adding ship {} to board {}".format(ship.name, self.name))
			print("Board {} shipMap started as:".format(self.name))
			print(self.shipMap)

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
		if debug == True:
			print("Addship complete.  Board {} shipMap is now:".format(self.name))
			print(self.shipMap)


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
# Helper Functions
###########################
def makeHeader(headings, spacer = None, empty = " "):
	"""
	Generate a header with each element of heading printed vertically in a column.

	For function call:
	makeHeader([0,1,2,3,4,5,6,7,8,9,10,11,12,13], spacer='-', empty='x')
	Output is a 2D list like:
		xxxxxxxxxx1111      <--tens (x's are empty char)
		01234567890123      <--ones
		--------------      <--spacer
	Headings can also be strings or floating point numbers

	:param headings: List of headings (strings, numbers)
	:param spacer: Character to use as a spacer (if len(spacer)>1, characters will be printed in sequence)
	:param empty: Character to use as filler for all empty space (must be single character)
	:return: 2D list
	"""
	if not len(str(empty)) == 1:
		raise ValueError("Input argument \"empty\" must be single character")
	else:
		empty = str(empty)

	# Convert headings into all strings
	headings = [str(x) for x in headings]

	# Define size of array.  rows is max heading length, cols is number of headings
	rows = max([len(x) for x in headings])
	cols = len(headings)

	# Initialize return list
	headerLst = [[empty for x in range(cols)] for y in range(rows)]

	# Fill heading numbers into return list
	for j,head in enumerate(headings):
		revhead = head[::-1]

		for i,char in enumerate(revhead):
			headerLst[-1 - i][j] = char

	# Add spacer if required
	if not spacer == None:
		for char in spacer:
			headerLst.append([char for x in range(cols)])

	return headerLst

def lstTranspose(lst):
	"""
	Transposes a 2D list

	:param lst:  2D list to transpose
	:return: Transpose of the input lst
	"""
	return [[lst[row][col] for row in range(0,len(lst))] for col in range(0,len(lst[0]))]



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