def printArgs(exclude = None):
	"""Prints the named and unnamed positional arguments passed to the function
	 calling printArgs.

	 Printing is of the format:
	    namedArg1: namedArg1_value  <--sorted list of named arguments and values, one per line
	    namedArg2: namedArg2_value
	    ...
		[unnamedArg1, unnamedArg2, ...] <--list of unnamed argument values

	Function inspired by: http://kbyanc.blogspot.com/2007/07/python-aggregating-function-arguments.html


	:param exclude: List of argument names that should be excluded for the
					reporting.
					Useful if you use this in a method of a class that is
					called by __repr__, because if you do not exclude "self"
					from that printing you get an infinite loop (__repr__ calls
					printArgs, which then tries to print self, which calls
					__repr__, ...)
	"""
	# Update default exclude to list
	if exclude == None:
		exclude = []

	# Collect the arguments from the parent function using arguments()
	fname, namedArgs, unnamedArgs = arguments(levelsUp=2)

	# Remove any excluded variables from the named args
	for ex in exclude:
		namedArgs.pop(ex, None)

	print("Function \'{}\' called with:".format(fname))
	print("\tNamed arguments:")
	for arg in sorted(namedArgs):
		print("\t\t{}: {}".format(arg, namedArgs[arg]))
	print("\tPositional arguments:")
	print("\t\t" + str(unnamedArgs))

	# Print exclusion list
	if len(exclude) > 0 and isinstance(exclude, list):
		print("\tExcluding any arguments with names:")
		for arg in sorted(exclude):
			print("\t\t{}".format(arg))



def arguments(levelsUp=1):
	"""
	Returns tuple containing dictionary of calling function's
	named arguments and a list of calling function's unnamed
	positional arguments.

	levelsUp sets how many frames above this function you want
	to look for arguments.  If you want to look at the function
	calling "arguments()", levelsUp=1.  For the parent function
	to the caller of "arguments()" (which is useful to make a
	portable printArguments function), set levelsUp=2

	Function inspired by: http://kbyanc.blogspot.com/2007/07/python-aggregating-function-arguments.html

	:param levelsUp: Number of frames above this frame (that arguments is
					 running in) to look for function arguments.
					 levelsUp=0 gives arguments to "arguments" itself (trivial case)
					 levelsUp=1 gives arguments to caller of "arguments" func
					 levelsUp=2 gives arguments to caller of caller of "arguments" func
					    This is useful for the above wrapper function for tidy printing of arguments
	:return: Dictionary of named arguments, list of unnamed positional arguments
	"""
	from inspect import getargvalues, stack

	# Use try/finally because frame objects can have some ill effects on garbage
	# collection.
	# ref: https://docs.python.org/2/library/inspect.html#the-interpreter-stack
	fobj= stack()[levelsUp]
	try:
		fname = fobj.function
		posname, kwname, args = getargvalues(fobj.frame)[-3:]
		posargs = args.pop(posname, [])
		args.update(args.pop(kwname, []))
	finally:
		del fobj

	return fname, args, posargs

