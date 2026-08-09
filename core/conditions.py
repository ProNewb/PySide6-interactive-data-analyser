import pandas as pd


class Condition:

    def __init__(self, column, operator, value):

        self.column = column
        self.operator = operator
        self.value = value

    def evaluate(self, dataframe):

        series = dataframe[self.column]

        value = self.convert_value(series)

        if self.operator == "equals":
            return series == value

        elif self.operator == "not_equals":
            return series != value

        elif self.operator == "contains":
            return series.astype(str).str.contains(
                str(value),
                case=False,
                na=False
            )

        elif self.operator == "greater_than":
            return series > value

        elif self.operator == "less_than":
            return series < value

        elif self.operator == "greater_or_equal":
            return series >= value

        elif self.operator == "less_or_equal":
            return series <= value

        raise ValueError(
            f"Unknown operator: {self.operator}"
        )

    def convert_value(self, series):

        if pd.api.types.is_numeric_dtype(series):

            try:
                return float(self.value)

            except ValueError:
                raise ValueError(
                    f"'{self.value}' is not a valid number "
                    f"for column '{self.column}'"
                )

        return self.value