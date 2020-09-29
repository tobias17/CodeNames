from utils import loadModel

class Engine():
    def __init__(self, modelName):
        self.model = loadModel(modelName)