class Player(object):

	def __init__(self, name, board = None, opponent = None, playerType = "Human"):

		self.name = name
		self.board = board
		self.opponent = opponent
		self.playerType = playerType

	def setBoard(self, board):
		self.board = board

	def setOpponent(self, opponent):
		self.opponent = opponent

	def fire(self):
		print()
		print("Player {} attacking:")
		if self.playerType == 'Human':
			self.opponent.board.interactiveFire()
		elif playerType == 'AI':
			print("Computers don't know how to shoot...yet")
		print("Player {} attack complete:")


	def __repr__(self):
		display = "Player: {} ({})\n".format(str(self.name), str(self.playerType))
		if self.board is None:
			board = "None\n"
		else:
			board = "\n" + str(self.board)
		display = display + "Board: {}".format(board)
		try:
			display = display + "Opponent: {}\n".format(str(self.opponent.name))
		except AttributeError:
			display = display + "Opponent: {}\n".format("None")
		return display
