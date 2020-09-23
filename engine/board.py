from utils import log, getWords
import random

class Word():
	teamChars = {'blue': '<', 'red': '>', 'white': '-', 'black': '*'}

	def __init__(self, word, team, guessed=False):
		self.word = word
		self.team = team
		self.guessed = guessed
		self.char = self.teamChars[team]

	def toString(self, hidden):
		if self.guessed:
			return self.char * 13
		filler = ' ' if hidden else self.char
		return filler + self.word + filler * (12 - len(self.word))

class Board():
	def __init__(self, board=None):
		if board is None:
			words = getWords()
			sample = random.sample(words, 25)
			labels = Board.getLabelList()
			self.board = [Word(word, label) for (word, label) in zip(sample, labels)]
		else:
			self.board = board

	def getLabelList():
		labels = []
		for i in range(8):
			labels.append('red')
		for i in range(8):
			labels.append('blue')
		for i in range(7):
			labels.append('white')
		for i in range(1):
			labels.append('black')
		labels.append('red' if random.randint(0,1) == 0 else 'blue')
		random.shuffle(labels)
		return labels

	def toString(self, hidden=True):
		return '\n'.join([' '.join([self.board[x+y*5].toString(hidden) for x in range(5)]) for y in range(5)])

	def getWordsWithTag(self, tag):
		return [w.word for w in self.board if w.team == tag]

	def getOpposingWords(self, team):
		return self.getWordsWithTag('red' if team == 'blue' else 'blue')
