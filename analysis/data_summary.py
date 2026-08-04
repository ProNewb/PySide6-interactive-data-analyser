class DataSummary:

    def generate(self, dataframe):

        summary = {}
        if dataframe is not None:
            summary["rows"] = len(dataframe)
            summary["columns"] = len(dataframe.columns)

            summary["column_names"] = list(dataframe.columns)

            summary["dtypes"] = dataframe.dtypes.to_dict()

            summary["missing"] = (
                dataframe
                .isnull()
                .sum()
                .to_dict()
            )
            summary["duplicates"] = dataframe.duplicated().sum()

            summary["memory"] = dataframe.memory_usage(
                deep=True
            ).sum()

            summary["numeric"] = dataframe.select_dtypes(
                include="number"
            ).describe()

            summary["categorical"] = dataframe.select_dtypes(
                exclude="number"
            ).describe()
        return summary