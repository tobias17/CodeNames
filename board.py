from utils import log, get_words, Tags
import random

class Word():
	team_chars = {Tags.BLUE: '<', Tags.RED: '>', Tags.WHITE: '-', Tags.BLACK: '*'}

	def __init__(self, word, team, guessed=False):
		self.word = word
		self.team = team
		self.guessed = guessed
		self.char = self.team_chars[team]

	def to_string(self, hidden):
		if self.guessed:
			return self.char * 13
		filler = ' ' if hidden else self.char
		return filler + self.word + filler * (12 - len(self.word))

class Board():
	def __init__(self, board=None):
		if board is None:
			words = get_words()
			sample = random.sample(words, 25)
			labels = Board.get_label_list()
			self.board = [Word(word, label) for (word, label) in zip(sample, labels)]
		else:
			self.board = board
		self.starting_team = Tags.BLUE if len(self.get_words(Tags.BLUE)) > len(self.get_words(Tags.RED)) else Tags.RED

	def get_label_list():
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

	def to_string(self, hidden=True):
		return '\n'.join([' '.join([self.board[x+y*5].to_string(hidden) for x in range(5)]) for y in range(5)])

	def get_words(self, tag):
		return [w.word for w in self.board if w.team == tag and not w.guessed]

	def get_summary(self, team):
		return (
			self.get_words(team),
			self.get_words(Tags.invert(team)),
			self.get_words(Tags.WHITE),
			self.get_words(Tags.BLACK),
		)

	def fetch_word(self, word):
		word_list = [w for w in self.board if w.word.upper() == word.upper()]
		if len(word_list) == 0:
			return None
		return word_list[0]
