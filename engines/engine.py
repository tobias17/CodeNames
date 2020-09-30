from utils import loadModel

class Engine():
    def __init__(self, modelName):
        self.model = loadModel(modelName)

    def reset(self):
        pass

    def undo(self):
        pass