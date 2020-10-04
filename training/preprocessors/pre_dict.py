import re
from time import time

class Node():
    def __init__(self):
        self.children = {}
        self.ending = False

    def add_word(self, word, allw):
        if len(word) < 1:
            self.ending = True
            return
        if not word[0] in self.children:
            self.children[word[0]] = Node()
        self.children[word[0]].add_word(word[1:], allw)

    def contains(self, word):
        if len(word) < 1:
            return self.ending
        if word[0] in self.children:
            return self.children[word[0]].contains(word[1:])
        return False


class PreDict():
    name = 'p-dict'

    start_kill_chars = ['<', '*', '|', '{', '[', '}', '-', ':', '=', ';', '!', '&lt;', 'File:']
    strip_strings = ['&quot;', '&amp;', "'", ':', ',', '.', '|', '[', ']']

    def __init__(self):
        with open('dict.txt') as f:
            self.dict = f.read().split()
        self.root_node = Node()
        for word in self.dict:
            self.root_node.add_word(word, word)
        print('pre dict inited')

    def clean_line(self, line):
        line = line.strip()

        for start_kill_char in self.start_kill_chars:
            if line.startswith(start_kill_char):
                return ''

        line = line.lower()
        line = re.sub('[;:\-]', ' ', line)
        line = re.sub('[^a-z ]', '', line)

        ret_val = []
        for word in line.split():
            if self.root_node.contains(word):
                ret_val.append(word)

        if len(ret_val) <= 5:
            return ''

        return ' '.join(ret_val)

    def old_clean(self, line):
        t0 = time()
        line = line.strip()

        t1 = time()
        for start_kill_char in self.start_kill_chars:
            if line.startswith(start_kill_char):
                return '', (t0, t1, time(), time(), time())

        t2 = time()
        line = line.lower()
        line = re.sub('[;:\-]', ' ', line)
        line = re.sub('[^a-z ]', '', line)

        t3 = time()
        ret_val = []
        for word in line.split():
            if word in self.dict:
                ret_val.append(word)

        if len(ret_val) <= 5:
            return '', (t0, t1, t2, t3, time())

        return ' '.join(ret_val), (t0, t1, t2, t3, time())