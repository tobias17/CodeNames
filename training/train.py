import os, random, gzip, re, warnings
from sys import argv, path
from tqdm import tqdm
from time import time

path.append('..')
from utils import get_words

CORPUS = 'c-wikidump_p-dict'
CORPUS_FILE_PATH = f'corpus/{CORPUS}'
MODEL_SAVE_LOC = f'../models/{CORPUS}'
MODEL_NAME = 'word2vec'

N_WORKERS = 20
N_EPOCHS = 5
MIN_COUNT = 150
DIMENSIONS = 300
MAX_DISTANCE = 10

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
            corpus_files = [f for f in files if f.endswith('.txt')]
            break

        random.shuffle(corpus_files)

        f_out = gzip.open(corpus_path, 'wb')

        for i, corpus_file in tqdm(enumerate(corpus_files)):
            with open(f'{CORPUS_FILE_PATH}/{corpus_file}') as f:
                text = f.read()
                for r in replacements:
                    text = re.sub(r, replacements[r], text)
                text = text.split('\n')
                text_order = list(range(len(text)))
                random.shuffle(text_order)

                for i in text_order:
                    f_out.write(text[i].encode('utf-8'))
            if i >= 50:
                break
        f_out.close()


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

        model.train(text, total_examples=model.corpus_count, epochs=model.iter)
    else:
        model = gensim.models.word2vec.Word2Vec(
            text, size=DIMENSIONS, window=MAX_DISTANCE,
            min_count=MIN_COUNT, workers=N_WORKERS,
            alpha=alpha_start, min_alpha=alpha_stop,
            sg=1, hs=1, iter=N_EPOCHS)

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

    random.seed(100 + npass)

    corpus_name = f'corpus_{npass}.gz'
    corpus_path = f'{CORPUS_FILE_PATH}/combined/{corpus_name}'
    
    create_corpus(corpus_path)
    train(corpus_path, npass)



if __name__ == "__main__":
    main()