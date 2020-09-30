from utils import load_model

class Engine():
    def __init__(self, model_name):
        self.model = load_model(model_name)

    def reset(self):
        pass

    def undo(self):
        pass