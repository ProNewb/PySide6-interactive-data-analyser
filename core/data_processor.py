from dataclasses import dataclass
import operator
import pandas as pd
from core.conditions import Condition

from dataclasses import dataclass
from typing import Any
import numpy as np
class DataType:

    TYPES = (
        "string",
        "integer",
        "float",
        "boolean",
        "datetime",
        "category",
    )

    DEFAULT = "string"

    PANDAS_DTYPES = {
        "string": "string",
        "integer": "Int64",
        "float": "Float64",
        "boolean": "boolean",
        "datetime": "datetime64[ns]",
        "category": "category",
    }

    OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "//": operator.floordiv,
    "%": operator.mod,
    "**": operator.pow,
}
    TRANSFORM_OPERATIONS = {

        # -------------------------
        # Numeric single-column
        # -------------------------

        "round": {
            "label": "Round",
            "group": "Numeric",
            "mode": "single",
            "min_columns": 1,
            "max_columns": 1,
            "allowed_dtypes": {"numeric"},
        },

        "absolute": {
            "label": "Absolute value",
            "group": "Numeric",
            "mode": "single",
            "min_columns": 1,
            "max_columns": 1,
            "allowed_dtypes": {"numeric"},
        },

        "normalize": {
            "label": "Normalize",
            "group": "Numeric",
            "mode": "single",
            "min_columns": 1,
            "max_columns": 1,
            "allowed_dtypes": {"numeric"},
        },

        "standardize": {
            "label": "Standardize",
            "group": "Numeric",
            "mode": "single",
            "min_columns": 1,
            "max_columns": 1,
            "allowed_dtypes": {"numeric"},
        },

        "power": {
            "label": "Power",
            "group": "Numeric",
            "mode": "single",
            "min_columns": 1,
            "max_columns": 1,
            "allowed_dtypes": {"numeric"},
        },

        "modulus": {
            "label": "Modulus",
            "group": "Numeric",
            "mode": "single",
            "min_columns": 1,
            "max_columns": 1,
            "allowed_dtypes": {"numeric"},
        },

        # -------------------------
        # Text single-column
        # -------------------------

        "uppercase": {
            "label": "Uppercase",
            "group": "Text",
            "mode": "single",
            "min_columns": 1,
            "max_columns": 1,
            "allowed_dtypes": {"text"},
        },

        "lowercase": {
            "label": "Lowercase",
            "group": "Text",
            "mode": "single",
            "min_columns": 1,
            "max_columns": 1,
            "allowed_dtypes": {"text"},
        },

        "find_and_replace": {
            "label": "Find and replace",
            "group": "Text",
            "mode": "single",
            "min_columns": 1,
            "max_columns": 1,
            "allowed_dtypes": {"text"},
        },

        # -------------------------
        # Datetime single-column
        # -------------------------

        "extract_year": {
            "label": "Extract year",
            "group": "Date / Time",
            "mode": "single",
            "min_columns": 1,
            "max_columns": 1,
            "allowed_dtypes": {"datetime"},
        },

        "extract_month": {
            "label": "Extract month",
            "group": "Date / Time",
            "mode": "single",
            "min_columns": 1,
            "max_columns": 1,
            "allowed_dtypes": {"datetime"},
        },

        # -------------------------
        # Multi numeric
        # -------------------------

        "add": {
            "label": "Add columns",
            "group": "Numeric",
            "mode": "multi",
            "min_columns": 2,
            "max_columns": 2,
            "allowed_dtypes": {"numeric"},
            "destination": "new",
        },

        "subtract": {
            "label": "Subtract columns",
            "group": "Numeric",
            "mode": "multi",
            "min_columns": 2,
            "max_columns": 2,
            "allowed_dtypes": {"numeric"},
            "destination": "new",
        },

        "multiply": {
            "label": "Multiply columns",
            "group": "Numeric",
            "mode": "multi",
            "min_columns": 2,
            "max_columns": 2,
            "allowed_dtypes": {"numeric"},
            "destination": "new",
        },

        "divide": {
            "label": "Divide columns",
            "group": "Numeric",
            "mode": "multi",
            "min_columns": 2,
            "max_columns": 2,
            "allowed_dtypes": {"numeric"},
            "destination": "new",
        },
        "compare_difference": {
            "label": "Difference between columns",
            "group": "Numeric",
            "mode": "multi",
            "min_columns": 2,
            "max_columns": 2,
            "allowed_dtypes": {"numeric"},
            "destination": "new",
        },
            "z_score": {
                "label": "Z-score",
                "group": "Numeric",
                "mode": "single",
                "min_columns": 1,
                "max_columns": 1,
                "allowed_dtypes": {"numeric"},
            },
        # -------------------------
        # Multi datetime
        # -------------------------

        "difference": {
            "label": "Difference",
            "group": "Date / Time",
            "mode": "multi",
            "min_columns": 2,
            "max_columns": 2,
            "allowed_dtypes": {"datetime"},
            "destination": "new",
        },

        "days_between": {
            "label": "Days between",
            "group": "Date / Time",
            "mode": "multi",
            "min_columns": 2,
            "max_columns": 2,
            "allowed_dtypes": {"datetime"},
            "destination": "new",
        },

        "hours_between": {
            "label": "Hours between",
            "group": "Date / Time",
            "mode": "multi",
            "min_columns": 2,
            "max_columns": 2,
            "allowed_dtypes": {"datetime"},
            "destination": "new",
        },

        # -------------------------
        # Multi text
        # -------------------------

        "concatenate": {
            "label": "Concatenate",
            "group": "Text",
            "mode": "multi",
            "min_columns": 2,
            "max_columns": None,
            "allowed_dtypes": {"text"},
            "destination": "new",
        },

        # -------------------------
        # Encoding
        # -------------------------

        "one_hot_encoding": {
            "label": "One-hot encoding",
            "group": "Category",
            "mode": "multi",
            "min_columns": 1,
            "max_columns": 1,
            "allowed_dtypes": {
                "text",
                "category",
            },
        },

        # -------------------------
        # Type
        # -------------------------

        "astype": {
            "label": "Change type",
            "group": "Type",
            "mode": "single",
            "min_columns": 1,
            "max_columns": 1,
            "allowed_dtypes": {
                "numeric",
                "text",
                "datetime",
                "category",
                "boolean",
            },
        },


    }
    
    @classmethod
    def convert_value(cls, value, dtype):

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

        if dtype == "datetime":
            return pd.to_datetime(value, errors="raise")

        if dtype == "category":
            return str(value)

        raise ValueError(
            f"Unsupported data type: {dtype}"
        )  
    
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
    destination: str = "replace"
    new_column: str | None = None

    def describe(self):

        if self.destination == "new":
            target = self.new_column
        else:
            target = self.column

        return (
            f"Transform '{self.column}' "
            f"using {self.operation} "
            f"→ '{target}'"
        )

@dataclass
class MultiColumnTransformConfig:
    columns: list[str]
    operation: str
    value: Any = None
    new_column: str | None = None
    output_columns: list[str] | None = None
    drop_source: bool = False

    def describe(self):
        columns = ", ".join(map(str, self.columns))

        if self.output_columns:
            output = ", ".join(map(str, self.output_columns))
        elif self.new_column:
            output = self.new_column
        else:
            output = "replace"

        return (
            f"Transform '{self.operation}' "
            f"using ({columns}) → {output}"
        )
@dataclass
class CalculationOperand:
    type: str          # "column" or "constant"
    value: Any

    def describe(self):
        if self.type == "column":
            return str(self.value)

        return str(self.value)

@dataclass
class CalculationConfig:
    name: str
    operands: list[CalculationOperand]
    operators: list[str]

    def describe(self):
        expression = ""

        for index, operand in enumerate(self.operands):
            expression += operand.describe()

            if index < len(self.operators):
                expression += f" {self.operators[index]} "

        return (
            f"Calculate column '{self.name}' "
            f"using {expression}"
        )
            
@dataclass
class CalculatedColumnConfig: # potentiallyt being removed
    name: str
    operation: str
    columns: list
    expression: str = None
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


    def apply_transform(self, dataframe, config):

        if isinstance(config, TransformConfig):
            return self.transform(dataframe, config)

        if isinstance(config, MultiColumnTransformConfig):
            return self.transform_multiple(dataframe, config)

        if isinstance(config, CalculatedColumnConfig):
            return self.add_calculated_column(dataframe, config)

        if isinstance(config, CalculationConfig):
            return self.calculate(
                dataframe,
                config
            )
        
        raise TypeError(
            f"Unsupported transform configuration: "
            f"{type(config).__name__}"
        )

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

            value = DataType.convert_value(
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

        left_df = self._select_join_columns(
            left_df,
            config.left_columns,
            config.left_key
        )

        right_df = self._select_join_columns(
            right_df,
            config.right_columns,
            config.right_key
        )

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

    def _select_join_columns(self, dataframe, columns, key):
        if not columns:
            return dataframe

        selected = list(columns)

        if key not in selected:
            selected.insert(0, key)

        return dataframe.loc[:, selected]

    def _validate_transform(self, dataframe, config):

        if dataframe is None:
            raise ValueError("No dataset is available.")

        if config.column not in dataframe.columns:
            raise ValueError(
                f"Column '{config.column}' does not exist."
            )

        if config.destination not in {"replace", "new"}:
            raise ValueError(
                f"Unknown destination: {config.destination}"
            )

        if config.destination == "new":

            if not config.new_column:
                raise ValueError(
                    "A new column name is required."
                )

            if config.new_column in dataframe.columns:
                raise ValueError(
                    f"Column '{config.new_column}' already exists."
                )
        
    def transform(self, dataframe, config):
        self._validate_transform(dataframe, config)

        df = dataframe.copy()
        series = df[config.column]

        if (
            pd.api.types.is_numeric_dtype(series)
            and not pd.api.types.is_bool_dtype(series)
        ):
            transformed = self._transform_numeric(series, config)

        elif pd.api.types.is_string_dtype(series):
            transformed = self._transform_text(series, config)

        elif pd.api.types.is_datetime64_any_dtype(series):
            transformed = self._transform_datetime(series, config)

        else:
            transformed = self._transform_type(series, config)

        target = (
            config.column
            if config.destination == "replace"
            else config.new_column
        )

        df[target] = transformed

        return df

    def _transform_text(self, series, config):
        if config.operation == "uppercase":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Uppercase requires a text column: "
                    f"'{config.column}'."
                )

            transformed = series.str.upper()

        elif config.operation == "lowercase":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Lowercase requires a text column: "
                    f"'{config.column}'."
                )

            transformed = series.str.lower()

        elif config.operation == "title_case":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Title case requires a text column: "
                    f"'{config.column}'."
                )

            transformed = series.str.title()

        elif config.operation == "trim":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Trim requires a text column: "
                    f"'{config.column}'."
                )

            transformed = series.str.strip()

        elif config.operation == "remove_whitespace":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Remove whitespace requires a text column: "
                    f"'{config.column}'."
                )

            transformed = series.str.replace(
                r"\s+",
                "",
                regex=True
            )

        elif config.operation == "capitalize_first":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Capitalizing requires a text column: "
                    f"'{config.column}'."
                )

            text = series.str.strip()

            transformed = (
                text.str[:1].str.upper()
                + text.str[1:].str.lower()
            )
        elif config.operation == "length":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Length requires a text column: "
                    f"'{config.column}'."
                )

            transformed = series.str.len()

        elif config.operation == "regex_replace":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Regex replace requires a text column: "
                    f"'{config.column}'."
                )

            pattern = config.value.get("pattern")
            replacement = config.value.get("replacement")

            if pattern is None or replacement is None:
                raise ValueError(
                    "Both 'pattern' and 'replacement' must be provided "
                    "for regex replace."
                )

            transformed = series.str.replace(
                pattern,
                replacement,
                regex=True
            )

        elif config.operation == "substring":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Substring requires a text column: "
                    f"'{config.column}'."
                )

            start = config.value.get("start")
            end = config.value.get("end")

            if start is None or end is None:
                raise ValueError(
                    "Both 'start' and 'end' must be provided "
                    "for substring."
                )

            transformed = series.str.slice(start, end)

        elif config.operation == "replace":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Replace requires a text column: "
                    f"'{config.column}'."
                )

            old_value = config.value.get("old_value")
            new_value = config.value.get("new_value")

            if old_value is None or new_value is None:
                raise ValueError(
                    "Both 'old_value' and 'new_value' must be provided "
                    "for replace."
                )

            transformed = series.str.replace(
                old_value,
                new_value,
                regex=False
            )

        elif config.operation == "contains":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Contains requires a text column: "
                    f"'{config.column}'."
                )

            substring = config.value

            if substring is None:
                raise ValueError(
                    "'substring' must be provided for contains."
                )

            transformed = series.str.contains(
                substring,
                regex=False
            )

        elif config.operation == "startswith":  
            

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Startswith requires a text column: "
                    f"'{config.column}'."
                )

            prefix = config.value

            if prefix is None:
                raise ValueError(
                    "'prefix' must be provided for startswith."
                )

            transformed = series.str.startswith(prefix)

        elif config.operation == "endswith":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Endswith requires a text column: "
                    f"'{config.column}'."
                )

            suffix = config.value

            if suffix is None:
                raise ValueError(
                    "'suffix' must be provided for endswith."
                )

            transformed = series.str.endswith(suffix)

        elif config.operation == "count_occurrences":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Count occurrences requires a text column: "
                    f"'{config.column}'."
                )

            substring = config.value

            if substring is None:
                raise ValueError(
                    "'substring' must be provided for count_occurrences."
                )

            transformed = series.str.count(substring)

        elif config.operation == "find_index":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Find index requires a text column: "
                    f"'{config.column}'."
                )

            substring = config.value

            if substring is None:
                raise ValueError(
                    "'substring' must be provided for find_index."
                )

            transformed = series.str.find(substring)

        elif config.operation == "is_numeric":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Is numeric requires a text column: "
                    f"'{config.column}'."
                )

            transformed = series.str.isnumeric()

        elif config.operation == "is_alpha":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Is alpha requires a text column: "
                    f"'{config.column}'."
                )

            transformed = series.str.isalpha()

        elif config.operation == "is_alphanumeric":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Is alphanumeric requires a text column: "
                    f"'{config.column}'."
                )

            transformed = series.str.isalnum()

        elif config.operation == "is_lower":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Is lower requires a text column: "
                    f"'{config.column}'."
                )

            transformed = series.str.islower()

        elif config.operation == "is_upper":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Is upper requires a text column: "
                    f"'{config.column}'."
                )

            transformed = series.str.isupper()

        elif config.operation == "length":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Length requires a text column: "
                    f"'{config.column}'."
                )

            transformed = series.str.len()

        elif config.operation == "strip":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Strip requires a text column: "
                    f"'{config.column}'."
                )

            transformed = series.str.strip()

        elif config.operation == "pad":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Pad requires a text column: "
                    f"'{config.column}'."
                )

            width = config.value.get("width")
            side = config.value.get("side", "left")

            if width is None:
                raise ValueError(
                    "'width' must be provided for pad."
                )

            if side not in {"left", "right", "both"}:
                raise ValueError(
                    "'side' must be 'left', 'right', or 'both'."
                )

            transformed = series.str.pad(
                width=width,
                side=side
            )

        elif config.operation == "find_and_replace":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Find and replace requires a text column: "
                    f"'{config.column}'."
                )

            find_value = config.value.get("find")
            replace_value = config.value.get("replace")

            if find_value is None or replace_value is None:
                raise ValueError(
                    "Both 'find' and 'replace' must be provided "
                    "for find_and_replace."
                )

            transformed = series.str.replace(
                find_value,
                replace_value,
                regex=False
            )

        elif config.operation == "regex_extract":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Regex extract requires a text column: "
                    f"'{config.column}'."
                )

            pattern = config.value

            if pattern is None:
                raise ValueError(
                    "'pattern' must be provided for regex_extract."
                )

            transformed = series.str.extract(pattern)

        elif config.operation == "regex_match":
            
            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Regex match requires a text column: "
                    f"'{config.column}'."
                )

            pattern = config.value

            if pattern is None:
                raise ValueError(
                    "'pattern' must be provided for regex_match."
                )

            transformed = series.str.match(pattern)

        elif config.operation == "regex_search":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Regex search requires a text column: "
                    f"'{config.column}'."
                )

            pattern = config.value

            if pattern is None:
                raise ValueError(
                    "'pattern' must be provided for regex_search."
                )

            transformed = series.str.contains(pattern, regex=True)

        elif config.operation == "regex_findall":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Regex findall requires a text column: "
                    f"'{config.column}'."
                )

            pattern = config.value

            if pattern is None:
                raise ValueError(
                    "'pattern' must be provided for regex_findall."
                )

            transformed = series.str.findall(pattern)

        elif config.operation == "regex_replace_all":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Regex replace all requires a text column: "
                    f"'{config.column}'."
                )

            pattern = config.value.get("pattern")
            replacement = config.value.get("replacement")

            if pattern is None or replacement is None:
                raise ValueError(
                    "Both 'pattern' and 'replacement' must be provided "
                    "for regex_replace_all."
                )

            transformed = series.str.replace(
                pattern,
                replacement,
                regex=True
            )

        elif config.operation == "regex_extract_all":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Regex extract all requires a text column: "
                    f"'{config.column}'."
                )

            pattern = config.value

            if pattern is None:
                raise ValueError(
                    "'pattern' must be provided for regex_extract_all."
                )

            transformed = series.str.extractall(pattern)

        elif config.operation == "regex_replace":
            
            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Regex replace requires a text column: "
                    f"'{config.column}'."
                )

            pattern = config.value.get("pattern")
            replacement = config.value.get("replacement")

            if pattern is None or replacement is None:
                raise ValueError(
                    "Both 'pattern' and 'replacement' must be provided "
                    "for regex_replace."
                )

            transformed = series.str.replace(
                pattern,
                replacement,
                regex=True
            )


            #
        elif config.operation == "extract_substring":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Extract substring requires a text column: "
                    f"'{config.column}'."
                )

            start = config.value.get("start")
            end = config.value.get("end")

            if start is None or end is None:
                raise ValueError(
                    "Both 'start' and 'end' must be provided "
                    "for extract_substring."
                )

            transformed = series.str.slice(start, end)  

        elif config.operation == "replace_substring":

            if not pd.api.types.is_string_dtype(series):
                raise ValueError(
                    f"Replace substring requires a text column: "
                    f"'{config.column}'."
                )

            old_substring = config.value.get("old_substring")
            new_substring = config.value.get("new_substring")

            if old_substring is None or new_substring is None:
                raise ValueError(
                    "Both 'old_substring' and 'new_substring' must be provided "
                    "for replace_substring."
                )

            transformed = series.str.replace(
                old_substring,
                new_substring,
                regex=False
            )
            return transformed

    def _transform_type(self, series, config):

        if config.operation != "astype":
            raise ValueError(
                f"Unknown type operation: {config.operation}"
            )

        target_dtype = config.value

        if target_dtype not in DataType.PANDAS_DTYPES:
            raise ValueError(
                f"Unsupported target type: {target_dtype}"
            )

        try:

            if target_dtype == "datetime":

                return pd.to_datetime(
                    series,
                    errors="raise"
                )

            if target_dtype == "category":

                return series.astype("category")

            return series.astype(
                DataType.PANDAS_DTYPES[target_dtype]
            )

        except (TypeError, ValueError) as error:

            raise ValueError(
                f"Cannot convert '{config.column}' "
                f"to {target_dtype}: {error}"
            ) from error
    
    def _transform_datetime(self, series, config):

        operation = config.operation

        if operation == "extract_year":
            return series.dt.year

        elif operation == "extract_month":
            return series.dt.month

        elif operation == "extract_day":
            return series.dt.day

        elif operation == "extract_weekday":
            return series.dt.dayofweek

        elif operation == "extract_weekend":
            return series.dt.dayofweek >= 5

        elif operation == "extract_time":
            return series.dt.time

        elif operation == "extract_quarter":
            return series.dt.quarter

        elif operation == "extract_month_name":
            return series.dt.month_name()

        elif operation == "extract_day_name":
            return series.dt.day_name()

        elif operation == "extract_hour":
            return series.dt.hour

        elif operation == "extract_minute":
            return series.dt.minute

        elif operation == "extract_second":
            return series.dt.second

        elif operation == "extract_millisecond":
            return series.dt.microsecond // 1000

        elif operation == "extract_nanosecond":
            return series.dt.nanosecond

        elif operation == "extract_week":
            return series.dt.isocalendar().week

        elif operation == "extract_day_of_year":
            return series.dt.dayofyear

        raise ValueError(
            f"Unknown datetime operation: {operation}"
        )
            
    def _transform_numeric(self, series, config):

        operation = config.operation

        if operation == "round":
            return series.round(config.value)

        elif operation == "absolute":
            return series.abs()

        elif operation == "normalize":

            minimum = series.min()
            maximum = series.max()

            if pd.isna(minimum) or pd.isna(maximum):
                raise ValueError(
                    "Cannot normalize a column with no usable values."
                )

            if minimum == maximum:
                return pd.Series(
                    0.0,
                    index=series.index
                )

            return (
                (series - minimum)
                / (maximum - minimum)
            )

        elif operation in {"standardize", "z_score"}:

            mean = series.mean()
            std = series.std()

            if pd.isna(std) or std == 0:
                raise ValueError(
                    f"Cannot calculate {operation} because "
                    "the standard deviation is zero."
                )

            return (series - mean) / std

        elif operation == "rank":
            return series.rank()

        elif operation == "log":

            if (series <= 0).any():
                raise ValueError(
                    "Logarithm requires all values to be positive."
                )

            return np.log(series)

        elif operation == "exp":
            return np.exp(series)

        elif operation == "sqrt":

            if (series < 0).any():
                raise ValueError(
                    "Square root requires non-negative values."
                )

            return np.sqrt(series)

        elif operation == "cbrt":
            return np.cbrt(series)

        elif operation == "reciprocal":

            if (series == 0).any():
                raise ValueError(
                    "Cannot calculate reciprocal because "
                    "the column contains zero."
                )

            return 1 / series

        elif operation == "square":
            return series ** 2

        elif operation == "cube":
            return series ** 3

        elif operation == "power":
            return series ** config.value

        elif operation == "modulus":

            if config.value == 0:
                raise ValueError(
                    "Cannot calculate modulus by zero."
                )

            return series % config.value

        elif operation == "floor":
            return np.floor(series)

        elif operation == "ceil":
            return np.ceil(series)

        elif operation == "round_to":
            return series.round(config.value)

        elif operation == "clip":

            minimum, maximum = config.value

            return series.clip(
                lower=minimum,
                upper=maximum
            )

        elif operation == "cumulative_sum":
            return series.cumsum()

        elif operation in {"standardize", "z_score"}:

            mean = series.mean()
            std = series.std()

            if pd.isna(std) or std == 0:
                raise ValueError(
                    f"Cannot calculate {operation} because "
                    "the standard deviation is zero."
                )

            return (series - mean) / std
        
        raise ValueError(
            f"Unknown numeric operation: {operation}"
        )
          

            
    def calculate(self, dataframe, config):

        result = dataframe.copy()

        expression = self._build_expression(result, config)

        result[config.name] = expression

        return result

    def _build_expression(self, df, config):

        current = self._operand_value(df, config.operands[0])

        for op, operand in zip(config.operators, config.operands[1:]):

            right = self._operand_value(df, operand)

            current = DataType.OPERATORS[op](current, right)

        return current

    def _operand_value(self, df, operand):

        if operand.type == "column":
            return df[operand.value]

        return operand.value

    def transform_multiple(self, dataframe, config):

        if config.operation == "concatenate":
            return self._concatenate(dataframe, config)

        if config.operation == "days_between":
            return self._days_between(dataframe, config)

        if config.operation == "one_hot_encoding":
            return self._one_hot(dataframe, config)

        if config.operation == "compare_difference":
            return self._compare_difference(dataframe, config)
            

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

                value = DataType.convert_value(
                    value,
                    "boolean"
                )

            elif pd.api.types.is_integer_dtype(series):

                value = DataType.convert_value(
                    value,
                    "integer"
                )

            elif pd.api.types.is_float_dtype(series):

                value = DataType.convert_value(value, "float")

            elif pd.api.types.is_datetime64_any_dtype(series):

                value = DataType.convert_value(
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
    
    def rename_column(self, dataframe, config):

            if config.old_name not in dataframe.columns:
                raise ValueError(
                    f"Column '{config.old_name}' does not exist."
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

            result = result.rename(
                columns={
                    config.old_name: config.new_name
                }
            )

            return result

    def _require_columns(self, dataframe, columns):
        if not columns:
            raise ValueError("At least one source column is required.")

        missing = [
            column for column in columns
            if column not in dataframe.columns
        ]

        if missing:
            raise ValueError(
                f"Column(s) do not exist: {missing}"
            )


    def _require_column_count(self, columns, count, operation):
        if len(columns) != count:
            raise ValueError(
                f"{operation} requires exactly {count} column(s)."
            )



    def _require_numeric_series(self, series, name):
        if (
            not pd.api.types.is_numeric_dtype(series)
            or pd.api.types.is_bool_dtype(series)
        ):
            raise ValueError(
                f"'{name}' must be numeric."
            )


    def _require_datetime(self, dataframe, columns, operation):
        for column in columns:
            if not pd.api.types.is_datetime64_any_dtype(
                dataframe[column]
            ):
                raise ValueError(
                    f"{operation} requires datetime columns. "
                    f"'{column}' is not datetime."
                )


    def _require_string(self, dataframe, columns, operation):
        for column in columns:
            if not pd.api.types.is_string_dtype(
                dataframe[column]
            ):
                raise ValueError(
                    f"{operation} requires text columns. "
                    f"'{column}' is not text."
                )


    def _validate_new_column(self, dataframe, name):
        if not name:
            raise ValueError(
                "A new column name is required."
            )

        if name in dataframe.columns:
            raise ValueError(
                f"A column named '{name}' already exists."
            )

    def _require_column_range(
        self,
        columns,
        min_columns,
        max_columns,
        operation
    ):
        count = len(columns)

        if count < min_columns:
            raise ValueError(
                f"{operation} requires at least "
                f"{min_columns} column(s)."
            )

        if max_columns is not None and count > max_columns:
            raise ValueError(
                f"{operation} accepts at most "
                f"{max_columns} column(s)."
            )

    def _compare_difference(self, dataframe, config):
        self._require_columns(dataframe, config.columns)
        self._require_column_count(
            config.columns,
            2,
            "Difference between columns"
        )

        self._require_numeric_series(
            dataframe[config.columns[0]],
            config.columns[0]
        )

        self._require_numeric_series(
            dataframe[config.columns[1]],
            config.columns[1]
        )

        result = dataframe.copy()

        result[config.new_column] = (
            result[config.columns[0]]
            - result[config.columns[1]]
        )

        return result