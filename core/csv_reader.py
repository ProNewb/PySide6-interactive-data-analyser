
import csv

import pandas as pd


class CSVReader:
    """Read CSV files using ImportOptions."""

    def read(self, filename, options, preview=False):
        """
        Read a CSV using the supplied ImportOptions.

        When preview=True, only the first ten rows
        are loaded.
        """

        rows = 20 if preview else None

        dataframe = pd.read_csv(
            filename,
            header=options.header,
            delimiter=options.delimiter,
            nrows=rows,
        )

        # ------------------------------------------------------
        # Manual headers
        # ------------------------------------------------------

        if options.manual_headers:

            if len(options.manual_headers) == len(
                dataframe.columns
            ):

                dataframe.columns = (
                    options.manual_headers
                )

        # ------------------------------------------------------
        # Automatic dtype inference
        # ------------------------------------------------------

        if options.infer_types:

            dataframe = dataframe.convert_dtypes()

        # ------------------------------------------------------
        # Explicit dtype conversions
        #
        # Explicit choices are applied AFTER automatic
        # inference so the user's choice wins.
        # ------------------------------------------------------

        for column, dtype in (
            options.column_types or {}
        ).items():

            if column not in dataframe.columns:
                continue

            dataframe[column] = self.convert_dtype(
                dataframe[column],
                dtype,
            )

        return dataframe

    # ==========================================================
    # DTYPE CONVERSION
    # ==========================================================

    def convert_dtype(self, series, dtype):
        """Convert one pandas Series to a requested dtype."""

        if dtype == "Auto":
            return series

        if dtype == "String":

            return series.astype("string")

        if dtype == "Integer":

            return pd.to_numeric(
                series,
                errors="coerce",
            ).astype("Int64")

        if dtype == "Float":

            return pd.to_numeric(
                series,
                errors="coerce",
            )

        if dtype == "Boolean":

            return series.astype("boolean")

        if dtype == "Datetime":

            return pd.to_datetime(
                series,
                errors="coerce",
            )

        if dtype == "Category":

            return series.astype("category")

        return series

    # ==========================================================
    # DELIMITER
    # ==========================================================

    def detect_delimiter(self, filename):
        """Attempt to detect the CSV delimiter."""

        with open(
            filename,
            "r",
            newline="",
            encoding="utf-8-sig",
        ) as file:

            sample = file.read(2048)

        dialect = csv.Sniffer().sniff(
            sample
        )

        return dialect.delimiter
