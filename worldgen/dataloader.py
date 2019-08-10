import json

def getdata(filename):
	result = {}
	with open('%s.txt' % filename) as json_file:
		result = json.load(json_file)
	return result