import random, os
from utils import log, LogTypes, get_words, Tags, clear_screen
from board import Board
from engines.engine_stretch import StretchEngine

e = StretchEngine('v3')

def print_board(board, turn):
	team_char = board.board[0].team_chars[turn]
	print(f'{turn} team\'s turn')
	print(f'{len(board.get_words(turn))} words remaining (vs {len(board.get_words(Tags.invert(turn)))})')
	print(team_char * 13*5 + '\n')
	print(board.to_string(hidden=True))

def play_game():
	board = Board()
	turn = board.starting_team
	while True:
		print('Thinking...')
		word, amnt = e.gen_word(board.get_summary(turn))
		guess_rem = amnt + 1
		while True:
			clear_screen()
			print_board(board, turn)
			print(f'\nYour clue is: {word}, {amnt}')
			guess = input(f'What is your guess ({guess_rem} rem)? ')

			if guess.lower() in ['done', 'quit']:
				break

			board_word = board.fetch_word(guess)
			if board_word is None:
				input('Word not found on board.')
				continue

			board_word.guessed = True

			if board_word.team == Tags.BLACK:
				input(f'Uh oh! You guessed the assassin! {Tags.invert(turn)} team wins!')
				return

			if board_word.team == Tags.WHITE:
				input('You guess a neutral word.')
				break

			if board_word.team == Tags.invert(turn):
				input('You guessed an opposing team\'s word.')
				break

			if board_word.team == turn:
				if len(board.get_words(turn)) == 0:
					input(f'You got them all! {turn} team has won the game!')
					return
				else:
					input('You guessed it!')

			guess_rem -= 1
			if guess_rem <= 0:
				break
		turn = Tags.invert(turn)

def main():
	while True:
		e.reset()
		play_game()
		while True:
			clear_screen()
			resp = input('Play another? ([y]es/[n]o) ')
			if resp.lower() in ['y', 'yes']:
				break
			if resp.lower() in ['n', 'no']:
				return

if __name__ == "__main__":
	random.seed(100)
	log.verbosity = 0
	log.types = [
		LogTypes.AiReasoning,
		# LogTypes.AiDebug,
	]
	main()