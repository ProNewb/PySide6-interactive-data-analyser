from dataclasses import dataclass

import pandas as pd


@dataclass
class DuplicateOptions:

    columns: list
    keep: str = "first"
    case_sensitive: bool = True
    ignore_whitespace: bool = False

@dataclass
class MissingValueOptions:

    columns: list
    action: str
    method: str | None = None
    value: object = None


class DataCleaner:

    def clean_missing(self, dataframe, options):
        if not isinstance(options, MissingValueOptions):
            raise TypeError("options must be MissingValueOptions")

        columns = self._columns(dataframe, options.columns)
        result = dataframe.copy()

        if options.action == "drop":
            return result.dropna(subset=columns)

        if options.action != "fill":
            raise ValueError(
                f"Unsupported missing-value action: {options.action}"
            )

        if options.method == "constant":
            return result.fillna({column: options.value for column in columns})

        if options.method == "nan":
            return result

        if options.method not in {"mean", "median", "mode"}:
            raise ValueError(
                f"Unsupported missing-value method: {options.method}"
            )

        for column in columns:
            series = result[column]

            if options.method == "mean":
                if not self._supports_numeric_fill(series):
                    raise ValueError(
                        "Mean can only be used with numeric or datetime "
                        f"columns: {column}"
                    )
                fill_value = series.mean()
            elif options.method == "median":
                if not self._supports_numeric_fill(series):
                    raise ValueError(
                        "Median can only be used with numeric or datetime "
                        f"columns: {column}"
                    )
                fill_value = series.median()
            else:
                modes = series.mode(dropna=True)
                fill_value = modes.iloc[0] if not modes.empty else None

            if fill_value is not None and not pd.isna(fill_value):
                result[column] = series.fillna(fill_value)

        return result

    def find_duplicates(self, dataframe, options):
        if not isinstance(options, DuplicateOptions):
            raise TypeError("options must be DuplicateOptions")

        columns = self._columns(dataframe, options.columns)
        duplicate_values = dataframe.loc[:, columns].copy()

        if not options.case_sensitive or options.ignore_whitespace:
            for column in columns:
                duplicate_values[column] = duplicate_values[column].map(
                    lambda value: self._normalise_duplicate_value(
                        value,
                        case_sensitive=options.case_sensitive,
                        ignore_whitespace=options.ignore_whitespace
                    ),
                    na_action="ignore"
                )

        return duplicate_values.duplicated(keep=options.keep)

    def remove_duplicates(self, dataframe, options):
        if not isinstance(options, DuplicateOptions):
            raise TypeError("options must be DuplicateOptions")

        duplicate_mask = self.find_duplicates(dataframe, options)
        return dataframe.loc[~duplicate_mask].copy()

    @staticmethod
    def _normalise_duplicate_value(
        value,
        case_sensitive,
        ignore_whitespace
    ):
        if not isinstance(value, str):
            return value

        if ignore_whitespace:
            value = value.strip()

        if not case_sensitive:
            value = value.casefold()

        return value

    @staticmethod
    def _supports_numeric_fill(series):
        return (
            pd.api.types.is_numeric_dtype(series)
            or pd.api.types.is_datetime64_any_dtype(series)
        )

    @staticmethod
    def _columns(dataframe, columns):
        selected = list(dataframe.columns if columns is None else columns)

        if not selected:
            selected = list(dataframe.columns)

        missing = [column for column in selected if column not in dataframe]

        if missing:
            raise ValueError(
                f"Unknown column(s): {', '.join(map(str, missing))}"
            )

        if not selected:
            raise ValueError("At least one column is required")

        return selected