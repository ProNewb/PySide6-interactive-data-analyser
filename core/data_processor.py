import pandas as pd
from core.conditions import Condition





class DataProcessor:
    '''lass responsible for data operations'''
    def filter(self, dataframe, conditions):

        mask = conditions.evaluate(dataframe)

        return dataframe[mask]


    

    def aggregate(self, dataframe, aggregation):

        group_by = aggregation.group_by
        aggregations = aggregation.aggregations
        allowed_functions = {
                "mean",
                "min",
                "max",
                "sum",
                "count"
            }
        aggregation_dict = {}
        if not aggregation.group_by:
            raise ValueError("At least one group-by column is required.")

        if not aggregation.aggregations:
            raise ValueError("At least one aggregation is required.")

        for column, function in aggregations:

            if function not in allowed_functions:
                raise ValueError(
                    f"Unsupported aggregation function: {function}"
                )

            if column not in aggregation_dict:
                aggregation_dict[column] = []

            aggregation_dict[column].append(function)

        result = (
            dataframe
            .groupby(group_by)
            .agg(aggregation_dict)
            .reset_index()
        )

        new_columns = []

        for column in result.columns:

            if isinstance(column, tuple):

                parts = [
                    str(part)
                    for part in column
                    if str(part) != ""
                ]

                new_columns.append(
                    "_".join(parts)
                )

            else:

                new_columns.append(
                    str(column)
                )

        result.columns = new_columns

        return result