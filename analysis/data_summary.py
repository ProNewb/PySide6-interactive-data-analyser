class DataSummary:
    """Generate descriptive information about a DataFrame."""

    def generate(self, dataframe):
        """Return a dictionary containing dataset statistics."""

        if dataframe is None:
            return {}

        return {
            "rows": len(dataframe),
            "columns": len(dataframe.columns),
            "column_names": list(dataframe.columns),

            "dtypes": (
                dataframe
                .dtypes
                .to_dict()
            ),

            "missing": (
                dataframe
                .isnull()
                .sum()
                .to_dict()
            ),

            "duplicates": (
                dataframe
                .duplicated()
                .sum()
            ),

            "memory": (
                dataframe
                .memory_usage(deep=True)
                .sum()
            ),

            "numeric": dataframe.select_dtypes(
                include="number"
            ).describe(),

            "categorical": dataframe.select_dtypes(
                include=["object", "category"]
            ).describe(),

            "datetime": dataframe.select_dtypes(
                include=["datetime"]
            ).describe()
        }