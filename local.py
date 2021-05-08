import random, os
from utils import log, LogTypes, get_words, Tags, clear_screen
from board import Board
from engines.engine_stretch import StretchEngine
from engines.engine_heuristic import HeuristicEngine
from models.association_models import BasicModel, PosTaggedModel, NaiveModel, CombinedModel


# models = [
# 	PosTaggedModel('1', purge_tags_to=2),
# 	PosTaggedModel('29', purge_tags_to=2),
# 	BasicModel('82', name='model.bin', binary=True),
# 	PosTaggedModel('200', purge_tags_to=2),
# ]
# model = CombinedModel(models, selectCrit=CombinedModel.SELECT_AVERAGE)

# model = NaiveModel()

model = PosTaggedModel('200', purge_tags_to=2)

engine = HeuristicEngine(model, 'models/word_dict.txt')


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
		log(board.to_string(hidden=False).replace('\n', ' '), logtype=LogTypes.BoardDump)
		word, amnt = engine.gen_word(board.get_summary(turn))
		guess_rem = amnt + 1
		while True:
			clear_screen()
			print_board(board, turn)
			print(f'\nYour clue is: {word.upper()}, {amnt}')
			guess = input(f'What is your guess ({guess_rem} rem)? ')

			if guess.lower() in ['done', 'quit']:
				break

			board_word = board.fetch_word(guess)
			if board_word is None:
				input('Word not found on board.')
				continue
			if board_word.guessed:
				input('Word has already been guessed.')
				continue

			board_word.guessed = True

			if board_word.team == Tags.BLACK:
				input(f'Uh oh! You guessed the assassin! {Tags.invert(turn)} team wins!')
				return

			if board_word.team == Tags.WHITE:
				input('You guess a neutral word.')
				break

			if board_word.team == Tags.invert(turn):
				if len(board.get_words(Tags.invert(turn))) == 0:
					input(f'You guessed the last opposing team\'s word! {Tags.invert(turn)} team has won the game!')
					return
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
		engine.reset()
		play_game()
		while True:
			clear_screen()
			resp = input('Play another? (yes/no) ')
			if resp.lower() in ['y', 'yes']:
				break
			if resp.lower() in ['n', 'no']:
				return

if __name__ == "__main__":
	# random.seed(100)
	log.verbosity = 0
	log.types = [
		LogTypes.AiReasoning,
		# LogTypes.AiTop10,
		# LogTypes.BoardDump,
		# LogTypes.AiDebug,
	]
	main()