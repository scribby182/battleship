class Coord(object):
	"""

	"""
	def __init__(self, coord = None):

		# Get coordinate from user if not specified in call
		if coord == None:
			while True:
				# Prompt user for coord
				coord = []
				try:
					coord = (int(input("Row: ")), int(input("Col: ")))
					break
				except ValueError:
					print("Invalid target - row/col must be integers")
					continue

		# Use coord but check for validity
		try:
			# Check for correct length
			if not len(coord) == 2:
				raise ValueError("Coordinate not correct length.  Must be pairs of integers")
			elif not all([isinstance(c,int) for c in coord]):
				raise ValueError("Coordinate values not correct.  Must be pairs of integers")

			# A few ways to write the same thing... This is probably sloppy.
			# Is there a way to make these all refer to the same base values,
			# so if one changed all changed?
			self.x = coord[0]
			self.y = coord[1]
			self.r = self.x
			self.c = self.y
			self.coord = (self.x, self.y)
		except Exception as e:
			raise e


	def __repr__(self):
		return "({}, {})".format(self.x,self.y)