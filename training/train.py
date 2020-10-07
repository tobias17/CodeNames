import os, random
from sys import argv

seed = 100
random.seed(seed)

CORPUS_FILE_PATH = 'corpus/c-wikidump_p-dict'
TRIM_CORPUS = True


def main():
    if len(argv) != 2:
        print(f'Invalid args: python {argv[0]} npass')
        return
    if not argv[1].isdigit():
        print(f'Invalid args: python {argv[0]} npass -> npass must be int')
    npass = int(argv[1])

    corpus_files = []
    for path, dirs, files in os.walk(CORPUS_FILE_PATH):
        corpus_files = [f for f in files if f.endswith('.txt')]
        break

    random.shuffle(corpus_files)
    if TRIM_CORPUS: corpus_files = corpus_files[:10]
    print(corpus_files)

    corpus_name = f'corpus_{npass}.gz'
    corpus_path = f'{CORPUS_FILE_PATH}/combined/{corpus_name}'
    if os.path.exists(corpus_path):
        print(f'Using corpus {corpus_path}')
    else:
        print(f'Creating corpus {corpus_path}')


if __name__ == "__main__":
    main()