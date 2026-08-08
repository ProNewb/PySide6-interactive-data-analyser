class DataProcessor:

    def filter(self, dataframe, column, operator, value):

        if operator == "equals":
            return dataframe[dataframe[column] == value]

        elif operator == "not_equals":
            return dataframe[dataframe[column] != value]

        elif operator == "greater_than":
            return dataframe[dataframe[column] > value]

        elif operator == "less_than":
            return dataframe[dataframe[column] < value]

        elif operator == "contains":
            return dataframe[
                dataframe[column].astype(str).str.contains(
                    str(value),
                    case=False,
                    na=False
                )
            ]

        raise ValueError(
            f"Unsupported filter operator: {operator}"
        )