from dataclasses import dataclass

import pandas as pd
from core.conditions import Condition



@dataclass
class JoinConfig:
    left_key: str
    right_key: str
    join_type: str
    mode: str = "merge"
    ignore_index: bool = False
    group_key: str | None = None

    left_columns: list | None = None
    right_columns: list | None = None

    filter_conditions: object = None

    def describe(self):

        return (
            f"{self.mode.title()} {self.join_type.title()} "
            f"on {self.left_key} = {self.right_key}"

            + (
                f" grouped by {self.group_key}"
                if self.group_key
                else ""
            )

            + (
                "; ignore index"
                if self.ignore_index
                else ""
            )

            + (
                "; main columns: "
                + ", ".join(map(str, self.left_columns))
                if self.left_columns
                else ""
            )

            + (
                "; imported columns: "
                + ", ".join(map(str, self.right_columns))
                if self.right_columns
                else ""
            )

            + (
                "; filtered imported rows"
                if self.filter_conditions
                else ""
            )
        )


@dataclass
class TransformConfig:

    column: str
    operation: str
    value: object = None

    def describe(self):

        if self.operation == "round":
            return f"Transform: round {self.column} to {self.value} dp"

        if self.operation == "uppercase":
            return f"Transform: uppercase {self.column}"

        if self.operation == "remove_whitespace":
            return f"Transform: remove whitespace from {self.column}"

        if self.operation == "capitalize_first":
            return f"Transform: capitalize first letter of {self.column}"

        if self.operation == "astype":
            return f"Transform: cast {self.column} to {self.value}"

        return f"Transform: {self.operation} {self.column}"
    
class DataProcessor:
    '''lass responsible for data operations'''
    def filter(self, dataframe, conditions):

        try:
            mask = conditions.evaluate(dataframe)
        except (KeyError, TypeError) as error:
            raise ValueError(
                f"Invalid filter condition: {error}"
            ) from error

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

            if function in {"mean", "sum"}:
                series = dataframe[column]
                if (
                    not pd.api.types.is_numeric_dtype(series)
                    or pd.api.types.is_bool_dtype(series)
                ):
                    raise ValueError(
                        f"'{function}' can only be used with numeric "
                        f"column '{column}'."
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

    def join(self, left_df, right_df, config):

        # ----------------------------------
        # Filter imported data
        # ----------------------------------

        if config.filter_conditions is not None:
            try:
                right_df = right_df[
                    config.filter_conditions.evaluate(right_df)
                ]
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(
                    f"Invalid imported-data filter: {error}"
                ) from error

        # ----------------------------------
        # Select main dataset columns
        # ----------------------------------

        if config.left_columns:
            missing = [
                column
                for column in config.left_columns
                if column not in left_df.columns
            ]

            if missing:
                raise ValueError(
                    "Unknown main column(s): "
                    + ", ".join(map(str, missing))
                )

            left_df = left_df.loc[:, config.left_columns]

        # ----------------------------------
        # Select imported dataset columns
        # ----------------------------------

        if config.right_columns:
            missing = [
                column
                for column in config.right_columns
                if column not in right_df.columns
            ]

            if missing:
                raise ValueError(
                    "Unknown imported column(s): "
                    + ", ".join(map(str, missing))
                )

            right_df = right_df.loc[:, config.right_columns]

        # ----------------------------------
        # Group imported data
        # ----------------------------------

        if config.group_key is not None:

            if config.group_key not in right_df.columns:
                raise ValueError(
                    f"Unknown group key: '{config.group_key}'"
                )

            right_df = right_df.drop_duplicates(
                subset=[config.group_key],
                keep="first"
            )

        # ----------------------------------
        # Concatenate
        # ----------------------------------

        if config.mode == "concat":

            return pd.concat(
                [left_df, right_df],
                ignore_index=config.ignore_index
            )

        # ----------------------------------
        # Merge
        # ----------------------------------

        return left_df.merge(
            right_df,
            left_on=config.left_key,
            right_on=config.right_key,
            how=config.join_type
        )

    def transform(self, dataframe, config):

        df = dataframe.copy()
        series = df[config.column]

        if config.operation == "round":

            if (
                not pd.api.types.is_numeric_dtype(series)
                or pd.api.types.is_bool_dtype(series)
            ):
                raise ValueError(
                    f"Round can only be used with numeric column "
                    f"'{config.column}'."
                )

            df[config.column] = (
                df[config.column]
                .round(config.value)
            )

        elif config.operation == "uppercase":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Uppercase requires a text column: '{config.column}'."
                )

            df[config.column] = (
                df[config.column]
                .str.upper()
            )

        elif config.operation == "lowercase":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Lowercase requires a text column: '{config.column}'."
                )

            df[config.column] = (
                df[config.column]
                .str.lower()
            )

        elif config.operation == "trim":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Trim requires a text column: '{config.column}'."
                )

            df[config.column] = (
                df[config.column]
                .str.strip()
            )

        elif config.operation == "remove_whitespace":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Remove whitespace requires a text column: "
                    f"'{config.column}'."
                )

            df[config.column] = series.str.replace(
                r"\s+", "", regex=True
            )

        elif config.operation == "capitalize_first":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Capitalizing requires a text column: "
                    f"'{config.column}'."
                )

            df[config.column] = series.str.replace(
                r"^(\s*)(\S)",
                lambda match: match.group(1) + match.group(2).upper(),
                regex=True
            )

        elif config.operation == "astype":

            df[config.column] = (
                df[config.column]
                .astype(config.value)
            )

        else:
            raise ValueError("Unknown transform")

        return df