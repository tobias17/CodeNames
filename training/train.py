import os, random, gzip, re, warnings, logging
from sys import argv, path
from tqdm import tqdm
from time import time
from gensim.models.callbacks import CallbackAny2Vec

path.append('..')
from utils import get_words

CORPUS = 'f_wikidump-p_dict_v2'
CORPUS_FILE_PATH = f'corpus/{CORPUS}'
MODEL_SAVE_LOC = f'../models/training/{CORPUS}'
MODEL_NAME = 'dict'

N_WORKERS = 24
N_EPOCHS = 5
MIN_COUNT = 150
DIMENSIONS = 300
MAX_DISTANCE = 5

def create_corpus(corpus_path):
    if os.path.exists(corpus_path):
        print(f'Using corpus {corpus_path}')
    else:
        print(f'Creating corpus {corpus_path}')

        word_list = [w.lower() for w in get_words(prefix='../')]
        replacements = {}
        for word in word_list:
            if ' ' in word:
                replacements[word] = word.replace(' ', '_')

        corpus_files = []
        for path, dirs, files in os.walk(CORPUS_FILE_PATH):
            corpus_files = [f for f in files if f.endswith('.gz')]
            break

        random.shuffle(corpus_files)

        sentences = []
        for corpus_file in tqdm(corpus_files):
            with gzip.open(f'{CORPUS_FILE_PATH}/{corpus_file}', 'rb') as f_in:
                for line in f_in:
                    line = line.decode('utf-8').rstrip()
                    for r in replacements:
                        line = re.sub(rf'\b{r}\b', replacements[r], line)
                    sentences.append(line)
        
        sentence_order = list(range(len(sentences)))
        random.shuffle(sentence_order)

        print('writing corpus to file...')
        f_out = gzip.open(corpus_path, 'wb')
        for i in sentence_order:
            f_out.write((sentences[i] + '\n').encode('utf-8'))
        f_out.close()
        print('done writing corpus to file')

class EpochLogger(CallbackAny2Vec):
    '''Callback to log information about training'''

    def __init__(self):
        self.epoch = 0

    def on_epoch_begin(self, model):
        print("Epoch #{} start".format(self.epoch))
        self.s_time = time()

    def on_epoch_end(self, model):
        print("Epoch #{} end".format(self.epoch))
        print(f'Completed epoch in {(time() - self.s_time) / 60:.2f} minutes')
        self.epoch += 1

def train(corpus_path, npass):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        import gensim.models.word2vec

    text = gensim.models.word2vec.LineSentence(corpus_path)

    alpha_start = 0.025 - 0.005 * (npass - 1.) + 0.0001
    alpha_stop = 0.025 - 0.005 * npass + 0.0001
    if alpha_stop <= 0:
        print('Invalid npass gives negative learning rate')
        return
    print(f'Learning rate: {alpha_start:.4f} -> {alpha_stop:.4f}')

    t = time()
    if npass > 1:
        prev_name = f'{MODEL_SAVE_LOC}/{MODEL_NAME}.{npass - 1}'
        model = gensim.models.word2vec.Word2Vec.load(prev_name)

        model.workers = N_WORKERS
        model.iter = N_EPOCHS
        model.alpha = alpha_start
        model.min_alpha = alpha_stop
    else:
        model = gensim.models.word2vec.Word2Vec(
            size=DIMENSIONS, window=MAX_DISTANCE,
            min_count=MIN_COUNT, workers=N_WORKERS,
            alpha=alpha_start, min_alpha=alpha_stop,
            sg=1, hs=1, iter=N_EPOCHS)

        model.build_vocab(text, progress_per=10000)

    epoch_logger = EpochLogger()
    model.train(text, total_examples=model.corpus_count, epochs=model.iter, callbacks=[epoch_logger])
    model.callbacks = []

    print(f'finished training in {(time() - t) / 60:.2f} minutes')

    if not os.path.exists(MODEL_SAVE_LOC):
        os.makedirs(MODEL_SAVE_LOC)
    save_name = f'{MODEL_SAVE_LOC}/{MODEL_NAME}.{npass}'
    model.save(save_name)


def main():
    if len(argv) != 2:
        print(f'Invalid args: python {argv[0]} npass')
        return
    if not argv[1].isdigit():
        print(f'Invalid args: python {argv[0]} npass -> npass must be int')
    npass = int(argv[1])

    corpus_name = f'corpus_{npass}.gz'
    corpus_folder = f'{CORPUS_FILE_PATH}/combined'
    corpus_path = f'{corpus_folder}/{corpus_name}'
    if not os.path.exists(corpus_folder):
        os.makedirs(corpus_folder)
    
    random.seed(100 + npass)
    create_corpus(corpus_path)

    random.seed(100 + npass)
    train(corpus_path, npass)



if __name__ == "__main__":
    main()