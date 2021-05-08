from engines.engine import Engine
from utils import get_stem, log, LogTypes
from tqdm import tqdm

class HeuristicEngine(Engine):
    name = 'heuristic'
    veto_dist_perc = 0.75
    neg_dist_perc = 0.85
    neut_dist_perc = 0.95
    weak_clue_perc = 0.3

    def __init__(self, model, allowed_clues_path=None):
        self.model = model
        self.reset()
        self.load_allowed_clues(allowed_clues_path)
        self.clean_allowed_words()
    
    def clean_allowed_words(self):
        removal = []
        for word in self.allowed_clues:
            if not self.model.contains(word):
                removal.append(word)
        for word in removal:
            self.allowed_clues.remove(word)
    
    def gen_word(self, summary):
        if self.allowed_clues == None:
            print('Allowed word list not found')
            return

        summary = [[word.lower().replace(' ', '_') for word in word_set] for word_set in summary]

        illegal_stems = set()
        for word_set in summary:
            illegal_stems.update([get_stem(word) for word in word_set])

        clue_evals = {}
        for word in tqdm(self.allowed_clues):
            is_legal = True
            if word in self.given_clues or get_stem(word) in illegal_stems:
                is_legal = False
            for word_set in summary:
                for board_word in word_set:
                    if word in board_word or board_word in word:
                        is_legal = False
            if is_legal:
                clue_evals[word] = self.h(word, summary)
        
        sorted_clues = sorted(clue_evals.items(), key=lambda kv: kv[1], reverse=True)
        for i, value in enumerate(sorted_clues[:10]):
            log(f'{i+1} -> {value}', logtype=LogTypes.AiTop10)

        clue, words = sorted_clues[0]
        log(f'Clue: {clue} -> Words: {words}', logtype=LogTypes.AiReasoning)
        self.given_clues.append(clue)
        
        return clue, len(words[1])

    def h(self, clue, summary):
        friendly, opposing, white, black = summary

        friendly_sims = {}
        for word in friendly:
            friendly_sims[word] = self.model.similarity(word, clue)
        
        opposing_sim = max([self.model.similarity(word, clue) for word in opposing])
        white_sim = max([self.model.similarity(word, clue) for word in white])
        black_sim = max([self.model.similarity(word, clue) for word in black])

        strong_words = []
        weak_words = []
        for word in friendly_sims:
            sim = friendly_sims[word]
            if sim * self.veto_dist_perc > black_sim and sim * self.neg_dist_perc > opposing_sim:
                weak_words.append(word)
                if sim * self.neut_dist_perc > white_sim:
                    strong_words.append(word)

        strong_values = [(friendly_sims[word]*self.neut_dist_perc - max(opposing_sim, white_sim)) for word in strong_words]
        weak_values = [(friendly_sims[word]*self.neg_dist_perc - opposing_sim) for word in weak_words]

        heuristic = (sum(strong_values) + sum(weak_values)*self.weak_clue_perc)
        clue_words = sorted(weak_words, key=lambda v: friendly_sims[v], reverse=True)

        return heuristic, clue_words


