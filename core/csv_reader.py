import csv

import pandas as pd


class CSVReader:
    """Read and inspect CSV files using pandas."""

    def read(self, filename, options, preview=False):
        """
        Read a CSV file using the supplied import options.

        When preview is True, only the first ten rows are loaded.
        """

        # Limit the number of rows when generating a preview.
        rows = 10 if preview else None

        dataframe = pd.read_csv(
            filename,
            header=options.header,
            delimiter=options.delimiter,
            nrows=rows
        )

        # Replace automatically generated column names when
        # the user supplied their own headers.
        if options.manual_headers:

            dataframe.columns = options.manual_headers

        # Allow pandas to infer more appropriate data types.
        if options.infer_types:

            dataframe = dataframe.convert_dtypes()

        return dataframe

    def detect_delimiter(self, filename):
        """Attempt to detect the delimiter used by a CSV file."""

        with open(
            filename,
            "r",
            newline=""
        ) as file:

            sample = file.read(2048)

        dialect = csv.Sniffer().sniff(sample)

        return dialect.delimiter