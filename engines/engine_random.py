import random

def getWord(summary):
	friendly, opposing, white, black = summary
	return friendly[random.randint(0, len(friendly) - 1)]