from utils import log, getWords, Tags
import random

class Word():
	teamChars = {Tags.BLUE: '<', Tags.RED: '>', Tags.WHITE: '-', Tags.BLACK: '*'}

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
		self.startingTeam = Tags.BLUE if len(self.getWords(Tags.BLUE)) > len(self.getWords(Tags.RED)) else Tags.RED

	def getLabelList():
		labels = []
		for i in range(8):
			labels.append(Tags.RED)
		for i in range(8):
			labels.append(Tags.BLUE)
		for i in range(7):
			labels.append(Tags.WHITE)
		for i in range(1):
			labels.append(Tags.BLACK)
		labels.append(Tags.RED if random.randint(0,1) == 0 else Tags.BLUE)
		random.shuffle(labels)
		return labels

	def toString(self, hidden=True):
		return '\n'.join([' '.join([self.board[x+y*5].toString(hidden) for x in range(5)]) for y in range(5)])

	def getWords(self, tag):
		return [w.word for w in self.board if w.team == tag and not w.guessed]

	def getSummary(self, team):
		return (
			self.getWords(team),
			self.getWords(Tags.invert(team)),
			self.getWords(Tags.WHITE),
			self.getWords(Tags.BLACK),
		)

	def fetchWord(self, word):
		wordList = [w for w in self.board if w.word.upper() == word.upper()]
		if len(wordList) == 0:
			return None
		return wordList[0]

