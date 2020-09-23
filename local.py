from utils import log, getWords, Tags
from board import Board
from engines.engine_random import getWord
import random

if __name__ == "__main__":
	random.seed(100)
	
	b = Board()
	print(b.toString())
	print(getWord(b.getSummary(Tags.RED)))