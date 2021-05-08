import os, gzip
from time import time
from sys import path
import re
from multiprocessing import Pool
from functools import partial

root = '../../../'
path.append(root)
from utils import get_words

folder_path = f'{root}models/naive'
cipher_name = 'cipher.txt'
cipher_path = f'{folder_path}/{cipher_name}'
model_name = 'freq.txt'
model_path = f'{folder_path}/{model_name}'
load_location = f'{root}training/corpus/f_wikidump-p_dict_v3'
dict_path = f'{root}models/word_dict.txt'

COUNT_KEYWORD = '__count__'

nthreads = 24
chunk_size = 100000
req_outer_freq_count = 500
req_inner_freq_count = 50
req_inner_freq_perc = 0.001


def _process_chunk(word_dict, text):
    word_freq = {}
    for line in text:
        words = set()
        for match in re.findall(r'\b[^ ]+\b', line):
            if match in word_dict:
                words.add(match)
        for outer_word in words:
            if outer_word not in word_freq:
                word_freq[outer_word] = {}
                word_freq[outer_word][COUNT_KEYWORD] = 1
            else:
                word_freq[outer_word][COUNT_KEYWORD] += 1
            for inner_word in words:
                if inner_word != outer_word:
                    if inner_word not in word_freq[outer_word]:
                        word_freq[outer_word][inner_word] = 1
                    else:
                        word_freq[outer_word][inner_word] += 1
    return word_freq

def combine_word_freq_sets(word_freq_sets_combined):
    outer_keys = set()
    for word_freq_sets_chunk in word_freq_sets_combined:
        outer_keys.update(word_freq_sets_chunk.keys())
    print(f'found {len(outer_keys)} unique words')

    word_freq = {}
    for outer_key in outer_keys:
        word_freq[outer_key] = {}
        inner_keys = set()
        for word_freq_sets_chunk in word_freq_sets_combined:
            if outer_key in word_freq_sets_chunk:
                inner_keys.update(word_freq_sets_chunk[outer_key].keys())
        for inner_key in inner_keys:
            word_freq[outer_key][inner_key] = 0
            for word_freq_sets_chunk in word_freq_sets_combined:
                if outer_key in word_freq_sets_chunk and inner_key in word_freq_sets_chunk[outer_key]:
                    word_freq[outer_key][inner_key] += word_freq_sets_chunk[outer_key][inner_key]
    return word_freq

def process_files():

    word_list = [w.lower() for w in get_words(prefix=root)]
    replacements = {}
    for word in word_list:
        if ' ' in word:
            replacements[word] = word.replace(' ', '_')
    print(f'found {len(replacements)} replacements')

    word_dict = set()
    with open(dict_path) as f:
        for line in f.read().split('\n'):
            line = line.split(' ')
            if len(line) > 1:
                word_dict.add(line[0])
    word_dict.update([w .replace(' ', '_') for w in word_list])
    print(f'loaded in a dictionary with {len(word_dict)} unique words')

    master_word_freq_set = {}
    for filename in os.listdir(load_location):
        if not filename.endswith('.gz'):
            continue
        s_time = time()

        texts = [ [] ]
        with gzip.open(f'{load_location}/{filename}', 'rb') as f_in:
            cntr = 0
            for line in f_in:
                line = line.decode('utf-8').rstrip()
                for r in replacements:
                    line = re.sub(rf'\b{r}\b', replacements[r], line)
                texts[-1].append(line)
                cntr += 1
                if cntr >= chunk_size:
                    # if cntr >= nthreads:
                    #     break
                    texts.append([])
                    cntr = 0
        print(f'{len(texts)} chunks of size {chunk_size} loaded in {int(time()-s_time)}s')

        s_time = time()
        process_chunk_partial = partial(_process_chunk, word_dict)
        with Pool(nthreads) as pool:
            word_freq_sets_combined = pool.map(process_chunk_partial, texts)
        print(f'processed text in {int(time()-s_time)}s')

        print('combining frequencies...')
        s_time = time()
        word_freq_sets_combined.append(master_word_freq_set)
        master_word_freq_set = combine_word_freq_sets(word_freq_sets_combined)
        print(f'combined in {int(time()-s_time)}s')
    
    print('purging down...')
    remaining_words = set()
    for outer_key in list(master_word_freq_set.keys()):
        if master_word_freq_set[outer_key][COUNT_KEYWORD] < req_outer_freq_count:
            del master_word_freq_set[outer_key]
        else:
            for inner_key in list(master_word_freq_set[outer_key].keys()):
                if master_word_freq_set[outer_key][inner_key] < req_inner_freq_count or master_word_freq_set[outer_key][inner_key] / master_word_freq_set[outer_key][COUNT_KEYWORD] < req_inner_freq_perc:
                    del master_word_freq_set[outer_key][inner_key]
            remaining_words.update(master_word_freq_set[outer_key].keys())
            if len(master_word_freq_set[outer_key]) <= 1:
                del master_word_freq_set[outer_key]
    remaining_words.update(master_word_freq_set.keys())
    remaining_words = list(remaining_words)
    word_cipher = {}
    for i, word in enumerate(remaining_words):
        word_cipher[word] = i
    
    print(f'purged down to {len(master_word_freq_set)} outer words, writing to file...')
    with open(cipher_path, 'w') as f_out:
        f_out.write('\n'.join(remaining_words))
    with open(model_path, 'wb') as f_out:
        first = True
        for outer_key in master_word_freq_set:
            if first:
                first = False
            else:
                f_out.write(int_as_bytes(-1, 2))
            
            f_out.write(int_as_bytes(word_cipher[outer_key], 2))
            for inner_key in master_word_freq_set[outer_key]:
                f_out.write(int_as_bytes(word_cipher[inner_key], 2))
                f_out.write(int_as_bytes(master_word_freq_set[outer_key][inner_key], 4))

            # line = f'{word_cipher[outer_key]}'
            # for inner_key in master_word_freq_set[outer_key]:
            #     line += f',{word_cipher[inner_key]},{master_word_freq_set[outer_key][inner_key]}'
            # f_out.write(line)

def int_as_bytes(value, b):
    return value.to_bytes(b, byteorder='big', signed=True)

def main():
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    if not os.path.exists(load_location):
        print(f'Load location not found -> {load_location}')
        return
    if not os.path.exists(dict_path):
        print(f'Dictionary file not found -> {dict_path}')
        return
    process_files()

if __name__ == "__main__":
    main()