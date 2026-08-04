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

        return df