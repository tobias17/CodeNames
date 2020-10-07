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


class WebDriver():

    def __init__(self, site):
        chrome_options = Options()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

        self.driver.get(site)

    def quit(self):
        self.driver.close()

    def gen_clue(self, turn, swap_teams, send_clue):
        try:
            if swap_teams:
                self.switch_teams()

            cover_locs = []
            for cover in self.driver.find_elements_by_class_name('tokenWrapper'):
                cover_locs.append(cover.location)

            words = []
            for tile in self.driver.find_elements_by_class_name('card'):
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
            print(f'given clues: {e.given_clues}')

            if not send_clue:
                return

            input_boxes = self.driver.find_elements_by_name('clue')
            if len(input_boxes) == 0:
                print('input box not found')
                return
            input_boxes[0].send_keys(word)

            amount_box = self.driver.find_element_by_class_name('numberSelectWrapper')
            amount_box.click()
            [b for b in amount_box.find_elements_by_class_name('option') if b.text == str(amnt)][0].click()

            time.sleep(1)
            self.driver.find_element_by_class_name('jsx-1776081540').click()

        except Exception as ex:
            print(f'Exception occured in generating a clue -> {ex}')

    def init(self):
        red_team_board = self.driver.find_element_by_id('teamBoard-red')
        red_team_board.find_elements_by_class_name('jsx-198695588')[4].click()
        print('inited to the read team')

    def reset(self, team_is_on):
        red_team_board = self.driver.find_element_by_id(f'teamBoard-{team_is_on.lower()}')
        red_team_board.find_element_by_class_name('jsx-198695588').click()
        print(f'joined as spymaster on team {team_is_on}')

    def switch_teams(self):
        self.driver.find_element_by_class_name('jsx-3037563900').click()
        self.driver.find_element_by_class_name('jsx-445627889').click()


def main(driver):
    team_is_on = Tags.EMPTY
    while True:
        text = input('What would you like to do? ').lower().strip()
        if 'red' == text or 'blue' == text:
            if team_is_on == Tags.EMPTY:
                print('Please init first')
            else:
                turn = Tags.RED if 'red' in text else Tags.BLUE
                driver.gen_clue(turn, team_is_on != turn, True)
                team_is_on = turn
        elif 'reset' == text:
            e.reset()
            driver.reset(team_is_on)
            print('done reseting')
        elif 'quit' == text:
            return
        elif 'given' == text:
            e.print_state()
        elif 'undo' == text:
            e.undo()
            e.print_state()
        elif 'init' == text:
            if team_is_on == Tags.EMPTY:
                driver.init()
                team_is_on = Tags.RED
            else:
                print(f'Currently on team {team_is_on}')
        elif text.startswith('set '):
            text = text[4:]
            if text.startswith('team '):
                text = text[5:]
                if text == 'red':
                    team_is_on = Tags.RED
                    print('Switched to Red team')
                elif text == 'blue':
                    team_is_on = Tags.BLUE
                    print('Switched to Blue team')
                elif text == 'empty':
                    team_is_on = Tags.EMPTY
                    print('Cleared team var')
                else:
                    print('Invalid format: set team [red/blue/empty]')
            else:
                print('Invalid format: set [team] value')

if __name__ == "__main__":
    if not len(sys.argv) == 2:
        print(f'Invalid args: python {sys.argv[0]} room_name')
    else:
        room_name = sys.argv[1]
        driver = WebDriver(f'https://codenames.game/room/{room_name}')

        print('')
        time.sleep(1)

        random.seed(100)
        log.verbosity = 0

        main(driver)

        driver.quit()
