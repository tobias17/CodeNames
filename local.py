from utils import log, getWords
from engine.board import Board

if __name__ == "__main__":
	b = Board()
	print(b.getWordsWithTag('blue'))
	print(b.getOpposingWords('red'))