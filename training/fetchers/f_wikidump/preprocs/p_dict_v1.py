import re, os
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


class PreProc():
    name = 'p_dict_v1'
    parent = 'f_wikidump'

    start_kill_chars = ['<', '*', '|', '{', '[', '}', '-', ':', '=', ';', '!', '&lt;', 'File:']
    strip_strings = ['&quot;', '&amp;', "'", ':', ',', '.', '|', '[', ']']

    def __init__(self):
        with open('preprocs/dict_v1.txt') as f:
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
        for word in line.split(' '):
            if self.root_node.contains(word):
                ret_val.append(word)

        if len(ret_val) <= 5:
            return ''

        return ' '.join(ret_val)