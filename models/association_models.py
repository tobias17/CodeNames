import warnings, re, itertools, os
with warnings.catch_warnings():
    warnings.simplefilter("ignore", UserWarning)
    import gensim
    from gensim.models.keyedvectors import KeyedVectors

class SimilarityModel():
    def contains(self, word):
        pass # returns if a word is in the model

    def similarity(self, word1, word2):
        pass # returns the highest similarity score between 2 words

class SearchingModel(SimilarityModel):
    def get_tags(self, word):
        pass # returns all tags related to a word
    
    def get_most_similar(self, words, topn):
        pass # returns the top n most similar words to a vector

    def tag_to_string(self, tag):
        pass # returns the string identifier of a tag

    def load_translation_table(self, folder, filename):
        filepath = f'models/{folder}/{filename}'
        if os.path.exists(filepath):
            self.translation_table = {}
            with open(filepath) as f_in:
                for line in f_in.read().split('\n'):
                    words = line.split(' ')
                    if len(words) > 0:
                        self.translation_table[words[0]] = words[1:]
        else:
            self.translation_table = None


class BasicModel(SearchingModel):
    def __init__(self, folder, name='word2vec', tt_name='translation_table.txt', binary=False, prefix='models'):
        if binary:
            self.model = KeyedVectors.load_word2vec_format(f'{prefix}/{folder}/{name}', binary=True)
        else:
            self.model = gensim.models.word2vec.Word2Vec.load(f'{prefix}/{folder}/{name}')
        self.load_translation_table(folder, tt_name)
    
    def contains(self, word):
        return word in self.model

    def get_tags(self, word):
        if self.translation_table and word in self.translation_table:
            return self.translation_table[word]
        return (word,)
    
    def get_most_similar(self, words, topn):
        return self.model.most_similar(positive=[(word, 1.0,) for word in words], topn=topn)

    def similarity(self, word1, word2):
        return self.model.similarity(word1, word2)
    
    def tag_to_string(self, tag):
        return tag.lower


class PosTaggedModel(SearchingModel):
    pos = ['NOUN', 'VERB', 'PROPN', 'ADJ']

    def __init__(self, folder, name='model.bin', prefix='models', binary=True, purge_tags_to=2, tt_name='translation_table.txt', remove_capitals=True):
        self.model = KeyedVectors.load_word2vec_format(f'{prefix}/{folder}/{name}', binary=binary)
        self.purge_tags_to = purge_tags_to
        self.remove_capitals = remove_capitals
        self.lookup_cache = {}
        self.load_translation_table(folder, tt_name)
    
    def contains(self, word):
        return len(self.get_tags(word)) > 0

    def get_tags(self, word):
        if word not in self.lookup_cache:
            self.lookup_cache[word] = []

            tags_pre = [word]
            if self.translation_table and word in self.translation_table:
                tags_pre = self.translation_table[word]

            for tag_pre in tags_pre:
                for suffix in self.pos:
                    for tag in [f'{tag_pre}_{suffix}', f'{tag_pre[0].upper()}{tag_pre[1:]}_{suffix}']:
                        if tag not in self.lookup_cache[word] and tag in self.model:
                            self.lookup_cache[word].append(tag)
            
            if self.remove_capitals:
                for tag_outer in list(self.lookup_cache[word]):
                    repeats = []
                    for tag_inner in self.lookup_cache[word]:
                        if tag_outer.lower() == tag_inner.lower():
                            repeats.append(tag_inner)
                    if len(repeats) > 1:
                        s = sorted(repeats, key=lambda w: self.model.vocab[w].count, reverse=True)
                        for tag in s[1:]:
                            if tag in self.lookup_cache[word]:
                                self.lookup_cache[word].remove(tag)

            if self.purge_tags_to > 0 and len(self.lookup_cache[word]) > self.purge_tags_to:
                ordered = sorted(self.lookup_cache[word], key=lambda x: self.model.vocab[x].count, reverse=True)
                self.lookup_cache[word] = ordered[:self.purge_tags_to]

        return self.lookup_cache[word]
    
    def get_most_similar(self, words, topn):
        return self.model.most_similar(positive=[(word, 1.0,) for word in words], topn=topn)

    def similarity(self, word1, word2):
        tags1 = self.get_tags(word1)
        tags2 = self.get_tags(word2)
        best_sim = 0.0
        for tag1, tag2 in itertools.product(tags1, tags2):
            sim = self.model.similarity(tag1, tag2)
            if sim > best_sim:
                best_sim = sim
        return best_sim
    
    def tag_to_string(self, tag):
        return re.sub(r'::|-', '_', tag.split('_')[0])


class NaiveModel():
    index_bits, freq_bits = 2, 4
    byteorder, signed = 'big', True

    def __init__(self, folder='naive', cipher='cipher.txt', freq='freq.txt'):
        self.load_model(folder, cipher, freq)

    def load_model(self, folder, cipher, freq):
        with open(f'models/{folder}/{cipher}') as f_in:
            self.cipher, self.cipher_T = {}, {}
            for i, word in enumerate(f_in.read().split('\n')):
                if word:
                    self.cipher[word] = i
                    self.cipher_T[i] = word
        self.icount = self.cipher['__count__']
        with open(f'models/{folder}/{freq}', 'rb') as f_in:
            self.freq = {}
            while True:
                outer_key = self.bytes_to_int(f_in.read(self.index_bits))
                self.freq[outer_key] = {}
                while True:
                    new_bytes = f_in.read(self.index_bits)
                    if new_bytes == b"":
                        return
                    inner_key = self.bytes_to_int(new_bytes)
                    if inner_key == -1:
                        break
                    inner_value = self.bytes_to_int(f_in.read(self.freq_bits))
                    self.freq[outer_key][inner_key] = inner_value

    def contains(self, word):
        return word in self.cipher

    def similarity(self, word1, word2):
        iword1, iword2 = self.cipher[word1], self.cipher[word2]
        if iword1 not in self.freq or iword2 not in self.freq or iword2 not in self.freq[iword1]:
            return 0
        value = self.freq[iword1][iword2]
        sim = max(value / self.freq[iword1][self.icount], value / self.freq[iword2][self.icount])
        if sim < 0.01:
            return NaiveModel.map(sim, 0, 0.01, 0.4, 0.6)
        if sim < 0.1:
            return NaiveModel.map(sim, 0.01, 0.1, 0.6, 0.8)
        return NaiveModel.map(sim, 0.1, 1.0, 0.8, 1.0)
    
    def map(value, oldMin, oldMax, newMin, newMax):
        return (((value - oldMin) * newMax) / (oldMax - oldMin)) + newMin

    def bytes_to_int(self, value):
        return int.from_bytes(value, byteorder=self.byteorder, signed=self.signed)


class CombinedModel(SimilarityModel):
    NEEDS_ALL, NEEDS_ALL_BUT_ONE = 'needs all', 'needs all but 1'
    SELECT_MIDDLE_UP, SELECT_AVERAGE, SELECT_MULTIPLY = 'select middle up', 'select average', 'select multiply'

    def __init__(self, models, containCrit=NEEDS_ALL_BUT_ONE, selectCrit=SELECT_MIDDLE_UP):
        self.models = models
        self.containCrit = containCrit
        self.selectCrit = selectCrit

    def contains(self, word):
        missCount = 0
        for model in self.models:
            if not model.contains(word):
                if self.containCrit == CombinedModel.NEEDS_ALL:
                    return False
                elif self.containCrit == CombinedModel.NEEDS_ALL_BUT_ONE and missCount > 0:
                    return False
                missCount += 1
        return True

    def similarity(self, word1, word2):
        sims = []
        for model in self.models:
            if model.contains(word1) and model.contains(word2):
                sims.append(model.similarity(word1, word2))

        if self.containCrit == CombinedModel.NEEDS_ALL and len(sims) < len(self.models):
            return 0.0
        elif self.containCrit == CombinedModel.NEEDS_ALL_BUT_ONE and len(sims) < len(self.models)-1:
            return 0.0
            
        sims = sorted(sims, reverse=True)
        if self.selectCrit == CombinedModel.SELECT_AVERAGE:
            return sum(sims)/len(sims)
        elif self.selectCrit == CombinedModel.SELECT_MULTIPLY:
            v = 1.0
            for sim in sims:
                v *= sim
            return v
        return sims[int(len(sims)/2 + 0.6) - 1]