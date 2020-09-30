from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from engines.engine_stretch import StretchEngine
from utils import Tags, clear_screen, log
from board import Board, Word
import time, random, sys

e = StretchEngine('v2')

INT_THRESH = 5

def does_intersect(loc1, loc2):
    return abs(loc1['x'] - loc2['x']) < INT_THRESH and abs(loc1['y'] - loc2['y']) < INT_THRESH

def gen_clue(turn, driver, swap_teams):
    try:
        if swap_teams:
            switch_teams(driver)

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
                if does_intersect(cover_loc, tile.location):
                    words[-1].guessed = True
                    break
        board = Board(board=words)

        clear_screen()
        print(board.to_string())

        print('\nThinking...')
        word, amnt = e.gen_word(board.get_summary(turn))
        print(f'\nYour clue is: {word}, {amnt}')

        input_boxes = driver.find_elements_by_name('clue')
        if len(input_boxes) == 0:
            print('input box not found')
            return
        input_boxes[0].send_keys(word)

        amount_box = driver.find_element_by_class_name('numberSelectWrapper')
        amount_box.click()
        [b for b in amount_box.find_elements_by_class_name('option') if b.text == str(amnt)][0].click()

        time.sleep(0.5)
        driver.find_element_by_class_name('jsx-1776081540').click()

    except Exception as ex:
        print(f'Exception occured in generating a clue -> {ex}')

def init(driver):
    red_team_board = driver.find_element_by_id('teamBoard-red')
    red_buttons = red_team_board.find_elements_by_class_name('jsx-198695588')
    red_buttons[4].click()
    print('inited to the read team')

def switch_teams(driver):
    driver.find_element_by_class_name('jsx-3037563900').click()
    driver.find_element_by_class_name('jsx-445627889').click()

def main(driver):
    team_is_on = Tags.EMPTY
    while True:
        text = input('What would you like to do? ')
        if 'red' in text.lower() or 'blue' in text.lower():
            if team_is_on == Tags.EMPTY:
                print('Please init first')
            else:
                turn = Tags.RED if 'red' in text.lower() else Tags.BLUE
                gen_clue(turn, driver, team_is_on != turn)
                team_is_on = turn
                continue
        if 'reset' in text.lower():
            e.reset()
            print('engine reset')
            continue
        if 'quit' in text.lower():
            return
        if 'given' in text.lower():
            print(f'Given clues: {e.given_clues}')
            continue
        if 'init' in text.lower():
            init(driver)
            team_is_on = Tags.RED
            continue

if __name__ == "__main__":
    if not len(sys.argv) == 2:
        print(f'Invalid args: python {sys.argv[0]} room_name')
    else:
        room_name = sys.argv[1]
        chrome_options = Options()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

        driver.get(f'https://codenames.game/room/{room_name}')

        print('')
        time.sleep(1)

        random.seed(100)
        log.verbosity = 0

        main(driver)
        driver.close()
