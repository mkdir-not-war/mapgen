from ingredients import ingredients, bases, brew

'''
actions:
	* heat (+1 heat level, -1 after 3 turns)
	* add
	* crush + add

NOTE: when two compounds react, the result's amount is double the minimum
of the amounts of the two compounds, with the greater amount having leftover
'''

def parseinput(userinput):
	if userinput == 'help':
		print('help!')
	elif userinput == 'quit':
		exit(1)

def main():
	potions = []
	print(vectorsbyclosestangle([10, 10], ([9, 10], [1, 1])))
	while(1):
		userinput = input('>> ')
		parseinput(userinput)

if __name__=='__main__':
	main()