import pandas as pd

class DataProcessor:

    def filter(
        self,
        dataframe,
        column,
        operator,
        value
    ):

        series = dataframe[column]

        if operator == "Equals":

            return dataframe[
                series == self.convert_value(
                    series,
                    value
                )
            ]

        elif operator == "Not equal":

            return dataframe[
                series != self.convert_value(
                    series,
                    value
                )
            ]

        elif operator == "Contains":

            return dataframe[
                series.astype(str).str.contains(
                    str(value),
                    case=False,
                    na=False
                )
            ]

        elif operator == "Greater than":

            return dataframe[
                series > float(value)
            ]

        elif operator == "Less than":

            return dataframe[
                series < float(value)
            ]

        elif operator == "Greater or equal":

            return dataframe[
                series >= float(value)
            ]

        elif operator == "Less or equal":

            return dataframe[
                series <= float(value)
            ]

        raise ValueError(
            f"Unsupported filter operator: {operator}"
        )

    def convert_value(self, series, value):

        if pd.api.types.is_numeric_dtype(series):

            return float(value)

        return value