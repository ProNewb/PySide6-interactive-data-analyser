class DataSummary:
    """Generate descriptive information about a DataFrame."""

    def generate(self, dataframe):

        if dataframe is None:
            return {}

        numeric = dataframe.select_dtypes(
            include="number"
        )

        categorical = dataframe.select_dtypes(
            include=["object", "category", "string"]
        )

        datetime = dataframe.select_dtypes(
            include=["datetime", "datetimetz"]
        )

        if len(numeric.columns) >= 2:
            correlations = numeric.corr()
        else:
            correlations = None

        column_summary = {}

        for column in dataframe.columns:

            column_summary[column] = {
                "dtype": str(dataframe[column].dtype),
                "missing": int(
                    dataframe[column].isna().sum()
                ),
                "unique": int(
                    dataframe[column].nunique()
                )
            }

        return {
            "rows": len(dataframe),

            "columns": len(dataframe.columns),

            "column_names": list(dataframe.columns),

            "dtypes": dataframe.dtypes.to_dict(),

            "missing": dataframe.isnull().sum().to_dict(),

            "missing_total": dataframe.isnull().sum().sum(),

            "duplicates": dataframe.duplicated().sum(),

            "memory": dataframe.memory_usage(
                deep=True
            ).sum(),

            "numeric": (
                numeric.describe()
                if not numeric.empty
                else None
            ),

            "categorical": (
                categorical.describe()
                if not categorical.empty
                else None
            ),

            "datetime": (
                datetime.describe()
                if not datetime.empty
                else None
            ),

            "correlations": correlations,
        
            "column_summary": column_summary

            }