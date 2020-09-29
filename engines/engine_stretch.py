from engines.engine import Engine
import random, time
from tqdm import tqdm
import utils
import itertools
import numpy as np

class StretchEngine(Engine):
    name = 'Stretch'

    def reset(self):
        self.givenClues = []

    def getWord(self, summary):
        saved_clues, best_score = self.get_clue_list_pair_stretch(summary)

        num_clues = len(saved_clues)
        order = sorted(range(num_clues), key=lambda k: best_score[k], reverse=True)

        clue, words = saved_clues[order[0]]
        clue_str = str(clue)[2:-1]
        self.givenClues.append(clue_str)
        return clue_str, len(words)
        
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
        utils.log(f'CLUE: {clue_words}', verbosity=2)
        utils.log(f' POS: {pos_words}', verbosity=2)
        utils.log(f' NEG: {neg_words}', verbosity=2)
        utils.log(f'VETO: {veto_words}', verbosity=2)

        # Initialize the list of illegal clues.
        illegal_words = list(pos_words) + list(neg_words) + list(veto_words)
        illegal_stems = set([utils.getStem(word) for word in illegal_words])

        clue_vectors = np.asarray([self.model[word.lower().replace(' ', '_')] for word in clue_words])

        mean_vector = clue_vectors.mean(axis=0)
        mean_vector /= np.sqrt(mean_vector.dot(mean_vector))

        closest = self.model.most_similar(positive=[mean_vector], topn=num_search)

        best_clue = None
        best_stretch = []
        max_min_cosine = -2.0
        for i in range(num_search):
            clue_str, dist = closest[i]
            clue_str = clue_str.lower()
            clue = clue_str.encode()

            for i in range(10):
                if str(i) in clue_str:
                    utils.log(f'num skipped {clue_str}')
                    continue

            if clue_str in self.givenClues:
                continue

            # clue = self.model.index2word[clue_index]
            # Ignore clues with the same stem as an illegal clue.
            if utils.getStem(clue) in illegal_stems:
                continue
            # Ignore clues that are contained within an illegal clue or
            # vice versa.
            contained = False
            for illegal in illegal_words:
                if clue_str.replace('_', ' ') in illegal.lower() or illegal.lower() in clue_str.replace('_', ' '):
                    contained = True
                    break
            if contained:
                continue
            # Manual override of clues not to give
            # TODO: make this not terrible, abstract out to file
            if clue_str not in self.model:
                # print('BREAK! BREAK! {}'.format(str(clue)[2:-1]))
                continue
            # Calculate the cosine similarity of this clue with all of the
            # positive, negative and veto words.
            clue_vector = self.model[clue_str]
            clue_cosine = [
                self.model.similarity(clue_str, word.lower().replace(' ', '_')) for word in clue_words
            ]
            pos_cosine = [
                self.model.similarity(clue_str, word.lower().replace(' ', '_')) for word in pos_words
            ]
            neg_cosine = [
                self.model.similarity(clue_str, word.lower().replace(' ', '_')) for word in neg_words
            ]
            neut_cosine = [
                self.model.similarity(clue_str, word.lower().replace(' ', '_')) for word in neut_words
            ]
            veto_cosine = [
                self.model.similarity(clue_str, word.lower().replace(' ', '_')) for word in veto_words
            ]
            # for cosine in (clue_cosine, neg_cosine, veto_cosine):
            #     print(cosine)

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
            best_clue = clue
            best_stretch = stretch_clues

        return best_clue, max_min_cosine, best_stretch