import random, os
from utils import log, getWords, Tags, clearScreen
from board import Board
from engines.engine_stretch import StretchEngine

e = StretchEngine('v2')

def printBoard(board, turn):
	teamChar = board.board[0].teamChars[turn]
	print(f'{turn} team\'s turn')
	print(f'{len(board.getWords(turn))} words remaining (vs {len(board.getWords(Tags.invert(turn)))})')
	print(teamChar * 13*5 + '\n')
	print(board.toString(hidden=True))

def playGame():
	board = Board()
	turn = board.startingTeam
	while True:
		print('Thinking...')
		word, amnt = e.getWord(board.getSummary(turn))
		guessRem = amnt + 1
		while True:
			clearScreen()
			printBoard(board, turn)
			print(f'\nYour clue is: {word}, {amnt}')
			guess = input(f'What is your guess ({guessRem} rem)? ')

			if guess.lower() in ['done', 'quit']:
				break

			boardWord = board.fetchWord(guess)
			if boardWord is None:
				input('Word not found on board.')
				continue

			boardWord.guessed = True

			if boardWord.team == Tags.BLACK:
				input(f'Uh oh! You guessed the assassin! {Tags.invert(turn)} team wins!')
				return

			if boardWord.team == Tags.WHITE:
				input('You guess a neutral word.')
				break

			if boardWord.team == Tags.invert(turn):
				input('You guessed an opposing team\'s word.')
				break

			if boardWord.team == turn:
				if len(board.getWords(turn)) == 0:
					input(f'You got them all! {turn} team has won the game!')
					return
				else:
					input('You guessed it!')

			guessRem -= 1
			if guessRem <= 0:
				break
		turn = Tags.invert(turn)

def main():
	while True:
		e.reset()
		playGame()
		while True:
			clearScreen()
			resp = input('Play another? ([y]es/[n]o) ')
			if resp.lower() in ['y', 'yes']:
				break
			if resp.lower() in ['n', 'no']:
				return

if __name__ == "__main__":
	random.seed(100)
	log.verbosity = 0
	main()