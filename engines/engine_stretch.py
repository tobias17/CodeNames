from engines.engine import Engine
import random, time, os
from tqdm import tqdm
import utils
import itertools
import numpy as np
import re

class StretchEngine(Engine):
    name = 'Stretch'

    def __init__(self, model, allowed_clues_path=None):
        self.model = model
        self.reset()
        self.load_allowed_clues(allowed_clues_path)

    def reset(self):
        self.given_clues = []

    def undo(self):
        if len(self.given_clues) > 0:
            self.given_clues = self.given_clues[:-1]

    def print_state(self):
        print(f'Given clues: {self.given_clues}')

    def gen_word(self, summary):
        saved_clues, best_score = self.get_clue_list_pair_stretch(summary)

        num_clues = len(saved_clues)
        order = sorted(range(num_clues), key=lambda k: best_score[k], reverse=True)

        clue, words = saved_clues[order[0]]
        utils.log(f'Clue: {clue} -> Words: {words}', logtype=utils.LogTypes.AiReasoning)
        for i in range(min(10, len(saved_clues))):
            ct10, wt10 = saved_clues[order[i]]
            utils.log(f'Score: {best_score[order[i]]}, Clue: {ct10} -> Words: {wt10}', logtype=utils.LogTypes.AiTop10)
        self.given_clues.append(clue)
        return clue, len(words)
        
    def get_clue_list_pair_stretch(self, summary, max_group=2, does_stretch=[2]):
        friendly, opposing, white, black = [np.array(s) for s in summary]

        num_words = len(friendly)
        best_score, saved_clues = [], []
        counts = range(min(num_words, max_group), 0, -1)
        groups_and_count = []
        for count in counts:
            for group in itertools.combinations(range(num_words), count):
                groups_and_count.append((group, count,))
        for group, count in tqdm(groups_and_count):
            bonus_factor = count ** 1.0
            words = friendly[list(group)]
            clue, score, stretch = self.get_clue_stretch(
                clue_words=words,
                pos_words=friendly,
                neg_words=opposing,
                neut_words=white,
                veto_words=black,
                give_stretch=(count in does_stretch),
            )
            if clue:
                best_score.append(score * bonus_factor)
                clue_words = words
                if stretch:
                    clue_words = np.concatenate((words, np.asarray(stretch)))
                saved_clues.append((clue, clue_words))
        return saved_clues, best_score

    def get_clue_stretch(
        self,
        clue_words,
        pos_words,
        neg_words,
        neut_words,
        veto_words,
        give_stretch=True,
        stretch_mult=1.10,
        veto_margin=0.2,
        num_search=100,
    ):
        utils.log(f'CLUE: {clue_words}', logtype=utils.LogTypes.AiDebug)
        utils.log(f' POS: {pos_words}', logtype=utils.LogTypes.AiDebug)
        utils.log(f' NEG: {neg_words}', logtype=utils.LogTypes.AiDebug)
        utils.log(f'VETO: {veto_words}', logtype=utils.LogTypes.AiDebug)

        # Initialize the list of illegal clues.
        illegal_words = list(pos_words) + list(neg_words) + list(veto_words)
        illegal_stems = set([utils.get_stem(word) for word in illegal_words])
        
        clues_tags = [self.model.get_tags(word.lower().replace(' ', '_')) for word in clue_words]

        best_clue = None
        best_stretch = []
        max_min_cosine = -2.0

        for clue_tags in itertools.product(*clues_tags):

            # clue_vectors = np.asarray(list(clue_vectors))
            # mean_vector = clue_vectors.mean(axis=0)
            # v1 = mean_vector.dot(mean_vector)
            # v2 = np.sqrt(v1)
            # mean_vector /= v2

            closest = self.model.get_most_similar(clue_tags, num_search)

            for i in range(min(len(closest), num_search)):
                clue_tag, dist = closest[i]
                clue_str = self.model.tag_to_string(clue_tag)
                utils.log(f'Evaluating: {clue_str}, {dist}', logtype=utils.LogTypes.AiDebug)

                if self.allowed_clues and clue_str not in self.allowed_clues:
                    utils.log('  clue not in allowed clues', logtype=utils.LogTypes.AiDebug)
                    continue

                if re.match(r'[^A-Za-z]', clue_str):
                    utils.log('  non-alpha skipped', logtype=utils.LogTypes.AiDebug)
                    continue

                if clue_str in self.given_clues:
                    utils.log('  already given', logtype=utils.LogTypes.AiDebug)
                    continue

                # clue = self.model.index2word[clue_index]
                # Ignore clues with the same stem as an illegal clue.
                if utils.get_stem(clue_str.encode()) in illegal_stems:
                    utils.log('  illegal stem', logtype=utils.LogTypes.AiDebug)
                    continue
                # Ignore clues that are contained within an illegal clue or
                # vice versa.
                contained = False
                for illegal in illegal_words:
                    if clue_str.replace('_', ' ') in illegal.lower() or illegal.lower() in clue_str.replace('_', ' '):
                        contained = True
                        break
                if contained:
                    utils.log('  illegal contained', logtype=utils.LogTypes.AiDebug)
                    continue
                # Manual override of clues not to give
                # TODO: make this not terrible, abstract out to file
                # if clue_str not in self.model:
                #     utils.log('  word not in model', logtype=utils.LogTypes.AiDebug)
                #     continue
                # else:
                #     utils.log('  FOUND IN MODEL', logtype=utils.LogTypes.AiDebug)

                # Calculate the cosine similarity of this clue with all of the
                # positive, negative and veto words.
                # clue_vectors = self.model.get_vectors(clue_str)

                clue_cosine = [self.model.similarity(clue_str, word.lower().replace(' ', '_')) for word in clue_words]
                neg_cosine =  [self.model.similarity(clue_str, word.lower().replace(' ', '_')) for word in neg_words]
                neut_cosine = [self.model.similarity(clue_str, word.lower().replace(' ', '_')) for word in neut_words]
                veto_cosine = [self.model.similarity(clue_str, word.lower().replace(' ', '_')) for word in veto_words]

                min_clue_cosine = np.min(clue_cosine)

                # Are all positive words more similar than any negative words?
                max_neg_cosine = -2.0
                if list(neg_words):
                    max_neg_cosine = np.max(neg_cosine)
                    if max_neg_cosine >= min_clue_cosine:
                        continue
                # Are all positive words more similar than any neutral words?
                max_neut_cosine = -2.0
                if list(neut_words):
                    max_neut_cosine = np.max(neut_cosine)
                    if max_neut_cosine >= min_clue_cosine:
                        continue
                # Is this word too similar to any of the veto words?
                max_veto_cosine = -2.0
                if list(veto_words):
                    max_veto_cosine = np.max(veto_cosine)
                    if max_veto_cosine >= min_clue_cosine - veto_margin:
                        continue
                # Check for potential stretch clues
                stretch_clues = []
                if give_stretch and list(pos_words):
                    for pos_word in pos_words:
                        if pos_word in clue_words:
                            continue
                        pos_word_sim = self.model.similarity(clue_str, pos_word.lower().replace(' ', '_'))
                        if pos_word_sim > max_neg_cosine and pos_word_sim > max_veto_cosine + veto_margin:
                            stretch_clues.append(pos_word)
                # Is this closer to all of the positive words than our previous best?
                min_clue_cosine *= pow(stretch_mult, len(stretch_clues))
                if min_clue_cosine < max_min_cosine:
                    continue
                # If we get here, we have a new best clue.
                max_min_cosine = min_clue_cosine
                best_clue = clue_str
                best_stretch = stretch_clues

        return best_clue, max_min_cosine, best_stretch