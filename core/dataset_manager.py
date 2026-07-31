import pandas as pd


class DatasetManager:

    def __init__(self):
        self.dataframe = None

    def load_csv(self, filename):
        self.dataframe = pd.read_csv(filename, header=None)

    def get_dataframe(self):
        return self.dataframe