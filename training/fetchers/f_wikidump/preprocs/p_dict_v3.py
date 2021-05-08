import re, os
from time import time, sleep

class PreProc():
    name = 'p_dict_v3'
    parent = 'f_wikidump'

    chars_req = 10
    pos = ['NOUN', 'ADJ']
    start_kill_chars = ['<', '*', '|', '{', '}', '-', ':', '=', ';', '!', '[[File:', 'File:', '[[Category:']
    strip_strings = ['&quot;', '&amp;', "'", ':', ',', '.', '|', '[', ']']

    def __init__(self):
        pass

    def clean_line(self, line):
        line = line.strip()

        line = re.sub('&amp;', '', line) # del &amp;
        line = re.sub('&quot;', '', line) # del &quot;
        line = re.sub('&lt;[^;]+&gt;', '', line) # del &lt;x&gt;

        for start_kill_char in self.start_kill_chars:
            if line.startswith(start_kill_char):
                return ''

        line = line.lower()
        line = re.sub('\[+([^|\]\[]+)\]+', '\g<1>', line) # [x] => x
        line = re.sub("'+([^']*)'+", '\g<1>', line) # 'x' => x
        line = re.sub('\[\[([^|\]\[]+)\|[^|\]\[]+\]\]', '\g<1>', line) # [x|y] => x
        line = re.sub('\(([^\)\[]+)\)', '\g<1>', line) # (x) => x
        line = re.sub('\{\{[^\{\}]+\}\}', '', line) # del {x}
        line = re.sub('https?://[^ ]* ', ' ', line) # del https?://x
        line = re.sub('&lt;[^;]+&gt;', '', line) # del &lt;x&gt; again
        line = re.sub("'s\b", '', line)
        line = re.sub("[:,.']", '', line)
        line = re.sub('  +', ' ', line) # '  +' => ' '

        if len(line.split(' ')) < self.chars_req:
            return ''

        words = []
        for word in line.split(' '):
            if re.match('^[a-z]+$', word):
                words.append(word)

        if len(words) < self.chars_req:
            return ''

        return ' '.join(words)

if __name__ == "__main__":
    pre = PreProc()
    first = True
    s_time = time()
    with open('test_text/p1.txt', encoding='utf-8') as in_file, open('test_text/p1_v3.txt', 'wb') as out_file:
        for i, line in enumerate(in_file.read().split('\n')):
            if i % 10000 == 0 and i > 0:
                print(f'{i} => {time() - s_time}s')
                s_time = time()
            clean_line = pre.clean_line(line)
            out_file.write((('\n' if not first else '') + clean_line).encode('utf-8'))
            first = False
