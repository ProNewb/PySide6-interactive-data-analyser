import pandas as pd


class Condition:
    """Represent a single condition used to filter a DataFrame."""

    def __init__(self, column, operator, value):

        # Column the condition applies to.
        self.column = column

        # Comparison operation to perform.
        self.operator = operator

        # Value supplied by the user.
        self.value = value

    def evaluate(self, dataframe):
        """
        Evaluate the condition against a DataFrame.

        Returns a pandas boolean Series indicating which rows
        satisfy the condition.
        """

        # Retrieve the column being tested.
        series = dataframe[self.column]

        # Convert the user-provided value to a suitable type.
        value = self.convert_value(series)

        if self.operator == "equals":

            return series == value

        if self.operator == "not_equals":

            return series != value

        if self.operator == "contains":

            return series.astype(str).str.contains(
                str(value),
                case=False,
                na=False
            )

        if self.operator == "greater_than":

            return series > value

        if self.operator == "less_than":

            return series < value

        if self.operator == "greater_or_equal":

            return series >= value

        if self.operator == "less_or_equal":

            return series <= value

        raise ValueError(
            f"Unknown operator: {self.operator}"
        )

    def convert_value(self, series):
        """Convert the input value to match a numeric column."""

        if pd.api.types.is_numeric_dtype(series):

            try:

                return float(self.value)

            except (ValueError, TypeError):

                raise ValueError(
                    f"'{self.value}' is not a valid number "
                    f"for column '{self.column}'"
                )

        # Non-numeric columns use the supplied value directly.
        return self.value