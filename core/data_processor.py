from dataclasses import dataclass

import pandas as pd
from core.conditions import Condition

from dataclasses import dataclass
from typing import Any


@dataclass
class FilterConfig:
    conditions: object

    def describe(self):
        return "Filter data"


@dataclass
class AggregationConfig:
    group_by: list
    aggregations: list

    def describe(self):
        group_text = ", ".join(map(str, self.group_by))

        aggregation_text = ", ".join(
            f"{column}: {function}"
            for column, function in self.aggregations
        )

        return (
            f"Aggregate by {group_text}; "
            f"{aggregation_text}"
        )


@dataclass
class MissingValueConfig:
    columns: list
    action: str
    method: str | None = None
    value: Any = None

    def describe(self):
        columns = ", ".join(map(str, self.columns))

        if self.action == "drop":
            return f"Drop rows with missing values in {columns}"

        if self.action == "fill":
            if self.method == "constant":
                return (
                    f"Fill missing values in {columns} "
                    f"with constant '{self.value}'"
                )

            return (
                f"Fill missing values in {columns} "
                f"using {self.method}"
            )

        return "Clean missing values"


@dataclass
class DuplicateConfig:
    columns: list

    def describe(self):
        columns = ", ".join(map(str, self.columns))

        return f"Remove duplicate rows based on {columns}"


@dataclass
class TransformConfig:
    column: str
    operation: str
    value: Any = None

    def describe(self):

        if self.operation == "round":
            return (
                f"Transform: round {self.column} "
                f"to {self.value} dp"
            )

        if self.operation == "uppercase":
            return f"Transform: uppercase {self.column}"

        if self.operation == "lowercase":
            return f"Transform: lowercase {self.column}"

        if self.operation == "trim":
            return f"Transform: trim {self.column}"

        if self.operation == "remove_whitespace":
            return (
                f"Transform: remove whitespace from "
                f"{self.column}"
            )

        if self.operation == "capitalize_first":
            return (
                f"Transform: capitalize first letter of "
                f"{self.column}"
            )

        if self.operation == "astype":
            return (
                f"Transform: cast {self.column} "
                f"to {self.value}"
            )

        return f"Transform: {self.operation} {self.column}"


@dataclass
class JoinConfig:
    left_key: str | None
    right_key: str | None
    join_type: str
    mode: str = "merge"
    ignore_index: bool = False
    group_key: str | None = None
    left_columns: list | None = None
    right_columns: list | None = None
    filter_conditions: object = None

    def describe(self):

        description = self.mode.title()

        if self.mode != "concat":
            description += (
                f" {self.join_type.title()} "
                f"on {self.left_key} = {self.right_key}"
            )

        if self.group_key:
            description += f" grouped by {self.group_key}"

        if self.ignore_index:
            description += "; ignore index"

        if self.left_columns:
            description += (
                "; main columns: "
                + ", ".join(map(str, self.left_columns))
            )

        if self.right_columns:
            description += (
                "; imported columns: "
                + ", ".join(map(str, self.right_columns))
            )

        if self.filter_conditions:
            description += "; filtered imported rows"

        return description
    
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

        left_df = left_df.copy()
        right_df = right_df.copy()

        # ----------------------------------
        # Filter right dataset
        # ----------------------------------

        if config.filter_conditions is not None:

            try:
                mask = config.filter_conditions.evaluate(right_df)
                right_df = right_df[mask]

            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(
                    f"Invalid right-dataset filter: {error}"
                ) from error

        # ----------------------------------
        # Group right dataset
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
        # Validate keys
        # ----------------------------------

        if config.left_key is None:
            raise ValueError("A left join key is required.")

        if config.right_key is None:
            raise ValueError("A right join key is required.")

        if config.left_key not in left_df.columns:
            raise ValueError(
                f"Unknown left join key: '{config.left_key}'"
            )

        if config.right_key not in right_df.columns:
            raise ValueError(
                f"Unknown right join key: '{config.right_key}'"
            )

        # ----------------------------------
        # Select columns
        # ----------------------------------

        if config.left_columns:
            left_df = left_df.loc[
                :,
                config.left_columns
            ]

        if config.right_columns:
            right_df = right_df.loc[
                :,
                config.right_columns
            ]

        # ----------------------------------
        # Remove duplicate right columns
        # ----------------------------------

        right_columns = []

        for column in right_df.columns:

            # Always keep the right key when the keys
            # have different names.
            if column == config.right_key:
                continue

            # Don't duplicate columns already present
            # in the left dataset.
            if column in left_df.columns:
                continue

            right_columns.append(column)

        right_df = right_df[
            [config.right_key] + right_columns
        ]

        # ----------------------------------
        # Merge
        # ----------------------------------

        if config.left_key == config.right_key:

            result = left_df.merge(
                right_df,
                on=config.left_key,
                how=config.join_type
            )

        else:

            result = left_df.merge(
                right_df,
                left_on=config.left_key,
                right_on=config.right_key,
                how=config.join_type
            )

        return result

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