import os, time, platform
import nltk.stem.wordnet

import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore", UserWarning)
    import gensim
    from gensim.models.keyedvectors import KeyedVectors

class LogTypes():
    AiReasoning = 'AiReasoning'
    AiDebug = 'AiDebug'
    AiTop10 = 'AiTop10'

def log(text, verbosity=0, logtype=None):
    tag = ''
    if logtype:
        if not logtype in log.types:
            return
        else:
            tag += ' - ' + logtype
    if verbosity > log.verbosity:
        return
    if not os.path.exists('logs'):
        os.makedirs('logs')
    if log.filename is None:
        date = time.strftime('%Y_%m_%d-%H_%M_%S')
        log.filename = f'logs/{date}.log'
    with open(log.filename, 'a+') as f:
        date = time.strftime('%m/%d/%Y %H:%M:%S')
        f.write(f'[{date}{tag}] {text}\n')
log.filename = None
log.verbosity = 0
log.types = []

def get_words(prefix=''):
    if get_words.words is None:
        with open(f'{prefix}words.txt') as f:
            get_words.words = f.read().splitlines()
    return get_words.words
get_words.words = None

class Tags():
    EMPTY = 'Empty'
    BLUE = 'Blue'
    RED = 'Red'
    WHITE = 'White'
    BLACK = 'Black'

    def invert(tag):
        return Tags.RED if tag == Tags.BLUE else Tags.BLUE

def load_model(name, filename):
    if name not in load_model.models:
        if filename.endswith('.bin'):
            load_model.models[name] = KeyedVectors.load_word2vec_format(f'models/{name}/{filename}', binary=True)

        else:
            load_model.models[name] = gensim.models.word2vec.Word2Vec.load(f'models/{name}/{filename}')
    return load_model.models[name]
load_model.models = {}

def get_stem(word):
        if word in ("pass", "passing", "passed",):
            return "pass"
        if word in ("microscope", "microscopy"):
            return "microscope"
        if word in ("mexico", "mexican", "mexicans", "mexicali"):
            return "mexico"
        if word in (
            "theater",
            "theatre",
            "theaters",
            "theatres",
            "theatrical",
            "theatricals",
        ):
            return "theater"
        if word in ("alp", "alps", "apline", "alpinist"):
            return "alp"
        return get_stem.lemmatizer.lemmatize(str(word))
get_stem.lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()

def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        sys.stdout.write(chr(27) + "[2J")