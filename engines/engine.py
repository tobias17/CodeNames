import os

class Engine():
    def reset(self):
        self.given_clues = []

    def undo(self):
        if len(self.given_clues) > 0:
            self.given_clues = self.given_clues[:-1]

    def load_allowed_clues(self, path):
        self.allowed_clues = None
        if path and os.path.exists(path):
            self.allowed_clues = set()
            with open(path) as f:
                for line in f.read().split('\n'):
                    words = line.split(' ')
                    if len(words) > 0:
                        self.allowed_clues.add(words[0])