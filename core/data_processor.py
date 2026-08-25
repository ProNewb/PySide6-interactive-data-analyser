from dataclasses import dataclass

import pandas as pd
from core.conditions import Condition

from dataclasses import dataclass
from typing import Any

@dataclass
class DeleteColumnConfig:
    columns: list

    def describe(self):
        return (
            f"Delete column(s): "
            + ", ".join(map(str, self.columns))
        )


@dataclass
class AddRowConfig:
    values: dict

    def describe(self):
        return "Add row"



@dataclass
class DuplicateRowConfig:
    rows: list

    def describe(self):
        return f"Duplicate {len(self.rows)} row(s)"
    
@dataclass
class AddColumnConfig:
    name: str
    value: Any = None
    dtype: str = "string"

    def describe(self):
        return (
            f"Add column '{self.name}' "
            f"({self.dtype})"
        )
    
@dataclass
class RenameColumnConfig:
    old_name: object
    new_name: str

    def describe(self):
        return f"Rename '{self.old_name}' to '{self.new_name}'"


@dataclass
class DuplicateColumnConfig:
    source: object
    new_name: str

    def describe(self):
        return f"Duplicate '{self.source}' as '{self.new_name}'"


@dataclass
class DeleteRowsConfig:
    rows: list

    def describe(self):
        return f"Delete {len(self.rows)} row(s)"

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
class CalculatedColumnConfig:
    name: str
    operation: str
    columns: list
    value: Any = None

    def describe(self):
        columns = ", ".join(map(str, self.columns))

        return (
            f"Calculate column '{self.name}' "
            f"using {self.operation} ({columns})"
        )

@dataclass
class JoinConfig:
    left_key: str | None
    right_key: str | None
    join_type: str
    mode: str = "merge"
    ignore_index: bool = False
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
    """Class responsible for data operations."""
    def add_column(self, dataframe, config):

        if not config.name:
            raise ValueError(
                "Column name cannot be empty."
            )

        if config.name in dataframe.columns:
            raise ValueError(
                f"A column named '{config.name}' already exists."
            )

        result = dataframe.copy()

        try:

            value = self.convert_value(
                config.value,
                config.dtype
            )

        except (TypeError, ValueError) as error:

            raise ValueError(
                f"Value '{config.value}' cannot be converted "
                f"to {config.dtype}."
            ) from error

        if config.dtype == "category":

            result[config.name] = pd.Series(
                [value] * len(result),
                index=result.index,
                dtype="category"
            )

        elif config.dtype == "date":

            result[config.name] = pd.Series(
                [value] * len(result),
                index=result.index,
                dtype="object"
            )

        elif config.dtype == "datetime":

            result[config.name] = pd.Series(
                [value] * len(result),
                index=result.index,
                dtype="datetime64[ns]"
            )

        else:

            result[config.name] = value

        return result

    def duplicate_column(self, dataframe, config):

        if config.source not in dataframe.columns:
            raise ValueError(
                f"Column '{config.source}' does not exist."
            )

        if not config.new_name:
            raise ValueError(
                "The new column name cannot be empty."
            )

        if config.new_name in dataframe.columns:
            raise ValueError(
                f"A column named '{config.new_name}' already exists."
            )

        result = dataframe.copy()

        result[config.new_name] = result[config.source].copy()

        return result


    def delete_rows(self, dataframe, config):

        if not config.rows:
            raise ValueError(
                "No rows were selected."
            )

        result = dataframe.copy()

        missing_rows = [
            row for row in config.rows
            if row not in result.index
        ]

        if missing_rows:
            raise ValueError(
                "One or more selected rows no longer exist."
            )

        result = result.drop(
            index=config.rows
        )

        return result
    
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

            target_dtype = config.value

            if target_dtype == "date":

                df[config.column] = pd.to_datetime(
                    df[config.column],
                    errors="raise"
                ).dt.normalize()

            elif target_dtype == "datetime":

                df[config.column] = pd.to_datetime(
                    df[config.column],
                    errors="raise"
                )

            elif target_dtype == "category":

                df[config.column] = (
                    df[config.column]
                    .astype("category")
                )

            else:

                try:

                    df[config.column] = (
                        df[config.column]
                        .astype(target_dtype)
                    )

                except (TypeError, ValueError) as error:

                    raise ValueError(
                        f"Cannot convert '{config.column}' "
                        f"to {target_dtype}."
                    ) from error

        return df

    def delete_column(self, dataframe, config):

        if not config.columns:
            raise ValueError(
                "No columns were selected."
            )

        missing = [
            column
            for column in config.columns
            if column not in dataframe.columns
        ]

        if missing:
            raise ValueError(
                f"Column(s) do not exist: {missing}"
            )

        if len(config.columns) >= len(dataframe.columns):
            raise ValueError(
                "You cannot delete all columns."
            )

        result = dataframe.drop(
            columns=config.columns
        )

        return result

    def add_row(self, dataframe, config):

        if dataframe is None:
            raise ValueError(
                "No dataset is available."
            )

        if not config.values:
            raise ValueError(
                "No row values were provided."
            )

        result = dataframe.copy()

        row = {}

        for column in dataframe.columns:

            value = config.values.get(
                column,
                None
            )

            series = dataframe[column]

            if pd.api.types.is_bool_dtype(series):

                value = self.convert_value(
                    value,
                    "boolean"
                )

            elif pd.api.types.is_integer_dtype(series):

                value = self.convert_value(
                    value,
                    "integer"
                )

            elif pd.api.types.is_float_dtype(series):

                value = self.convert_value(
                    value,
                    "float"
                )

            elif pd.api.types.is_datetime64_any_dtype(series):

                value = self.convert_value(
                    value,
                    "datetime"
                )

            elif pd.api.types.is_categorical_dtype(series):

                if value is not None:
                    value = str(value)

                    if value not in series.cat.categories:

                        result[column] = (
                            result[column]
                            .cat.add_categories([value])
                        )

            row[column] = value

        new_row = pd.DataFrame(
            [row],
            columns=dataframe.columns
        )

        result = pd.concat(
            [result, new_row],
            ignore_index=True
        )

        return result

    def duplicate_rows(self, dataframe, config):

        if not config.rows:
            raise ValueError(
                "No rows were selected."
            )

        missing = [
            row
            for row in config.rows
            if row not in dataframe.index
        ]

        if missing:
            raise ValueError(
                "One or more selected rows no longer exist."
            )

        rows_to_duplicate = dataframe.loc[
            config.rows
        ]

        result = pd.concat(
            [
                dataframe,
                rows_to_duplicate
            ]
        )

        return result

    def add_calculated_column(self, dataframe, config):

        if not config.name:
            raise ValueError(
                "Column name cannot be empty."
            )

        if config.name in dataframe.columns:
            raise ValueError(
                f"A column named '{config.name}' already exists."
            )

        if not config.columns:
            raise ValueError(
                "At least one source column is required."
            )

        missing = [
            column
            for column in config.columns
            if column not in dataframe.columns
        ]

        if missing:
            raise ValueError(
                f"Column(s) do not exist: {missing}"
            )

        result = dataframe.copy()

        if config.operation == "add":

            if len(config.columns) != 2:
                raise ValueError(
                    "Add requires two columns."
                )

            result[config.name] = (
                result[config.columns[0]]
                + result[config.columns[1]]
            )

        elif config.operation == "subtract":

            if len(config.columns) != 2:
                raise ValueError(
                    "Subtract requires two columns."
                )

            result[config.name] = (
                result[config.columns[0]]
                - result[config.columns[1]]
            )

        elif config.operation == "multiply":

            if len(config.columns) != 2:
                raise ValueError(
                    "Multiply requires two columns."
                )

            result[config.name] = (
                result[config.columns[0]]
                * result[config.columns[1]]
            )

        elif config.operation == "divide":

            if len(config.columns) != 2:
                raise ValueError(
                    "Divide requires two columns."
                )

            if (result[config.columns[1]] == 0).any():
                raise ValueError(
                    "Cannot divide by zero."
                )

            result[config.name] = (
                result[config.columns[0]]
                / result[config.columns[1]]
            )

        elif config.operation == "absolute":

            if len(config.columns) != 1:
                raise ValueError(
                    "Absolute requires one column."
                )

            result[config.name] = (
                result[config.columns[0]].abs()
            )

        elif config.operation == "round":

            if len(config.columns) != 1:
                raise ValueError(
                    "Round requires one column."
                )

            result[config.name] = (
                result[config.columns[0]]
                .round(config.value)
            )

        elif config.operation == "concatenate":

            if len(config.columns) != 2:
                raise ValueError(
                    "Concatenate requires two columns."
                )

            result[config.name] = (
                result[config.columns[0]].astype("string")
                + result[config.columns[1]].astype("string")
            )

        else:

            raise ValueError(
                f"Unknown calculated column operation: "
                f"{config.operation}"
            )

        return result
    def convert_value(self, value, dtype):
        """Convert a single value to the requested application dtype."""

        if value is None:
            return None

        if dtype == "string":
            return str(value)

        if dtype == "integer":
            return int(value)

        if dtype == "float":
            return float(value)

        if dtype == "boolean":

            if isinstance(value, bool):
                return value

            if isinstance(value, str):

                text = value.strip().lower()

                if text in ("true", "yes", "1"):
                    return True

                if text in ("false", "no", "0"):
                    return False

            raise ValueError(
                f"Value '{value}' cannot be converted to boolean."
            )

        if dtype == "date":

            converted = pd.to_datetime(
                value,
                errors="raise"
            )

            return converted.date()

        if dtype == "datetime":

            return pd.to_datetime(
                value,
                errors="raise"
            )

        if dtype == "category":
            return str(value)

        raise ValueError(
            f"Unsupported data type: {dtype}"
        )