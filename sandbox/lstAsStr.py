def lstAsStr(lst, colSep = "", rowSep = "\n"):
	"""
	Returns a string representation of a 2D list.

	NOTE: This probably is more complicated than it needs to be.  A simpler
	recursive solution should exist, even one that protects against lists that
	are too deep.

	:param colSep: Character to seperate each column element (default is "")
	:param rowSep: Character to seperate each row (default is newline)
	:return: String representation of the list

	"""

	# Check for valid input (is 1D or 2D list)
	if isinstance(lst,list):
		for row in lst:
			if isinstance(row,list):
				for col in row:
					if isinstance(col,list):
						raise TypeError("Error: List cannot have more than two dimensions")
					elif not (isinstance(col,str) or isinstance(col,int) or isinstance(col,float)):
						raise TypeError("Error: Base elements in list must be strings, integers, or floats")
	else:
		raise TypeError("Error: Input is not a list")

	output = ""
	for row in lst:
		print("processing row {}".format(row))
		try:
			output = output + colSep.join([str(x) for x in row]) + rowSep
		except:
			output = output + str(row) + rowSep
		print("Output string is now: \n{}\n".format(output))
	return output


#### Debug code
if __name__ == '__main__':
	lists = []
	lists.append([0,1,2,3])
	lists.append([[10,11,12],[20,21,22],[30,31,32]])
	lists.append([0,1,2,[50,51,52,[100,101]]])

	for i,lst in enumerate(lists):
		print("Printing test list {}".format(i))
		print(lstAsStr(lst))