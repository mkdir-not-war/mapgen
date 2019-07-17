import compounds
import effects
import ingredients

'''
actions:
	- heat (+1 heat level, -1 after 3 turns)
	- add
	- crush + add
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