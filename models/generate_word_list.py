from tqdm import tqdm
import re
import spacy
from multiprocessing import Pool
from time import time

nlp = spacy.load("en_core_web_sm")

class PreProc():
    name = 'p_dict_v2'
    parent = 'f_wikidump'

    chars_req = 10
    pos = ['NOUN', 'ADJ']
    start_kill_chars = ['<', '*', '|', '{', '}', '-', ':', '=', ';', '!', '[[File:', 'File:', '[[Category:']
    strip_strings = ['&quot;', '&amp;', "'", ':', ',', '.', '|', '[', ']']

    def __init__(self):
        self.word_freq = {}
        pass

    def save_words(self, line):
        line = line.strip()

        line = re.sub('&amp;', '', line) # del &amp;
        line = re.sub('&quot;', '', line) # del &quot;
        line = re.sub('&lt;[^;]+&gt;', '', line) # del &lt;x&gt;

        for start_kill_char in self.start_kill_chars:
            if line.startswith(start_kill_char):
                return ''

        line = re.sub('\[+([^|\]\[]+)\]+', '\g<1>', line) # [x] => x
        line = re.sub("'+([^']*)'+", '\g<1>', line) # 'x' => x
        line = re.sub('\[\[([^|\]\[]+)\|[^|\]\[]+\]\]', '\g<1>', line) # [x|y] => x
        line = re.sub('\(([^\)\[]+)\)', '\g<1>', line) # (x) => x
        line = re.sub('\{\{[^\{\}]+\}\}', '', line) # del {x}
        line = re.sub('https?://[^ ]* ', ' ', line) # del https?://x
        line = re.sub('&lt;[^;]+&gt;', '', line) # del &lt;x&gt; again
        line = re.sub('  +', ' ', line) # '  +' => ' '
        line = re.sub('[,.:]', '', line)
        line = re.sub("'s", '', line)

        for word in nlp(line):
            if re.match(r'[A-Z]{2}', word.text):
                continue
            text_lower = word.text.lower()
            if re.match(r'^[a-z]+$', text_lower):
                if word.pos_ in self.pos and re.search('[aeiouy]', text_lower):
                    if text_lower not in self.word_freq:
                        self.word_freq[text_lower] = 1
                    else:
                        self.word_freq[text_lower] += 1
                elif word.pos_ == 'VERB' and re.search('[aeiouy]', word.lemma_.lower()) and not word.lemma_.lower() == 'be':
                    if word.lemma_.lower() not in self.word_freq:
                        self.word_freq[word.lemma_.lower()] = 1
                    else:
                        self.word_freq[word.lemma_.lower()] += 1

nthreads = 24
nchunks = nthreads * 10

def calc_word_freq(lines):
    preproc = PreProc()
    for line in lines:
        preproc.save_words(line)
    return preproc.word_freq

def main():
    with open('../training/corpus/simple_wikipedia/unzipped/simplewiki-20210420-pages-meta-current.xml', 'rb') as f:
        text = f.read().decode('utf-8').split('\n')
        line_count = len(text)
        text = [text[int(i*line_count/nchunks):int((i+1)*line_count/nchunks)] for i in range(nchunks)]

        print('text loaded in, processing now')
        s_time = time()
        with Pool(nthreads) as pool:
            word_freq_combined = pool.map(calc_word_freq, text)
        print(f'finished processing in {time()-s_time}s')

    keys = set()
    for word_freq_chunk in word_freq_combined:
        keys.update(word_freq_chunk.keys())

    print(f'found {len(keys)} unique words')
    
    word_freq = {}
    for key in keys:
        word_freq[key] = 0
        for word_freq_chunk in word_freq_combined:
            if key in word_freq_chunk:
                word_freq[key] += word_freq_chunk[key]

    s = sorted(word_freq.items(), key=lambda k: k[1], reverse=True)
    # for i in range(len(s)):
    #     if s[i][1] < 5:
    #         break
    # s = s[:i]
    print(f'purged down to {len(s)} words, writing to file...')

    with open('words_v2.txt', 'w') as f:
        f.write('\n'.join([f'{x[0]} -> {x[1]}' for x in s]))

if __name__ == "__main__":
    main()