from engines.engine import Engine
import random, time
from tqdm import tqdm

class RandomEngine(Engine):
    name = 'Random'
    
    def getWord(self, summary):
        friendly, opposing, white, black = summary
        for i in tqdm(range(10)):
            time.sleep(0.1)
        return (friendly[random.randint(0, len(friendly) - 1)], random.randint(1, 1))