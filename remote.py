from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from engines.engine_stretch import StretchEngine
from utils import Tags, clearScreen, log
from board import Board, Word
import time, random, sys, logging

e = StretchEngine('v2')

INT_THRESH = 5

def doesIntersect(loc1, loc2):
    return abs(loc1['x'] - loc2['x']) < INT_THRESH and abs(loc1['y'] - loc2['y']) < INT_THRESH

def genClue(turn):
    try:
        cover_locs = []
        for cover in driver.find_elements_by_class_name('tokenWrapper'):
            cover_locs.append(cover.location)

        words = []
        for tile in driver.find_elements_by_class_name('card'):
            classes = tile.get_attribute('class')
            tag = Tags.EMPTY
            if 'red' in classes:
                tag = Tags.RED
            elif 'blue' in classes:
                tag = Tags.BLUE
            elif 'gray' in classes:
                tag = Tags.WHITE
            elif 'black' in classes:
                tag = Tags.BLACK
            words.append(Word(tile.text, tag))
            for cover_loc in cover_locs:
                if doesIntersect(cover_loc, tile.location):
                    words[-1].guessed = True
                    break
        board = Board(board=words)

        clearScreen()
        print(board.toString())

        print('\nThinking...')
        word, amnt = e.getWord(board.getSummary(turn))
        print(f'\nYour clue is: {word}, {amnt}')
    except Exception as ex:
        print(f'Exception occured in generating a clue -> {ex}')

def main():
    while True:
        turn = Tags.EMPTY
        while True:
            text = input('What would you like to do? ')
            if 'red' in text.lower():
                turn = Tags.RED
                break
            if 'blue' in text.lower():
                turn = Tags.BLUE
                break
            if 'reset' in text.lower():
                e.reset()
                print('engine reset')
                continue
            if 'quit' in text.lower():
                return
            if 'given' in text.lower():
                print(f'Given clues: {e.givenClues}')
        genClue(turn)

if __name__ == "__main__":
    if not len(sys.argv) == 2:
        print(f'Invalid args: python {sys.argv[0]} room_name')
    else:
        roomName = sys.argv[1]
        chrome_options = Options()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

        driver.get(f'https://codenames.game/room/{roomName}')

        print('')
        time.sleep(1)

        random.seed(100)
        log.verbosity = 0
        main()
