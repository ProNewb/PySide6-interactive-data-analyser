import pandas as pd
from core.conditions import Condition





class DataProcessor:

    def filter(self, dataframe, conditions):

        mask = conditions.evaluate(dataframe)

        return dataframe[mask]