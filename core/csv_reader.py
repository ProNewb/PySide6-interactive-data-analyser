import csv

import pandas as pd


class CSVReader:

    def read(self, filename, options, preview=False):

        rows = 10 if preview else None

        df = pd.read_csv(
            filename,
            header=options.header,
            delimiter=options.delimiter,
            nrows=rows
        )

        if options.manual_headers:
            df.columns = options.manual_headers


        if options.infer_types:

            df = df.convert_dtypes()

        return df

    def detect_delimiter(self, filename):

        with open(filename, "r") as file:

            sample = file.read(2048)

        dialect = csv.Sniffer().sniff(sample)

        return dialect.delimiter