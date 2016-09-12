def chooseFromList(message, choices, nullChoice=None, debug = True):
	print(message)
	if nullChoice is not None:
		print("Enter:\t{}".format(nullChoice))
	for i, choice in enumerate(choices):
		print("{}:\t{}".format(i, choice))
	while True:
		try:
			choice = input("-> ")
			if nullChoice is not None and choice == "":
				return nullChoice
			else:
				choice = int(choice)
		except ValueError:
			print("Invalid choice.  Please choose again")
			continue
		if choice in range(len(choices)):
			if debug == True:
				print("received valid choice {} corresponding to {}".format(choice, choices[choice]))
			break
		else:
			print("Invalid choice.  Please choose again")
			continue

	return choices[choice]