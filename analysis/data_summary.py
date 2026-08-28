import pandas as pd


class DataSummary:
    """Generate descriptive information about a DataFrame."""

    def generate(self, dataframe):

        if dataframe is None:
            return {}

        numeric = dataframe.select_dtypes(
            include="number"
        )

        categorical = dataframe.select_dtypes(
            include=[
                "object",
                "category",
                "string"
            ]
        )

        datetime = dataframe.select_dtypes(
            include=[
                "datetime",
                "datetimetz"
            ]
        )

        if len(numeric.columns) >= 2:
            correlations = numeric.corr()
        else:
            correlations = None

        column_summary = {}

        for column in dataframe.columns:

            series = dataframe[column]

            summary = {
                "dtype": str(series.dtype),
                "missing": int(
                    series.isna().sum()
                ),
                "missing_percent": (
                    series.isna().mean() * 100
                ),
                "unique": int(
                    series.nunique()
                ),
                "non_null": int(
                    series.notna().sum()
                ),
            }

            # -------------------------
            # Numeric
            # -------------------------

            if (
                pd.api.types.is_numeric_dtype(series)
                and not pd.api.types.is_bool_dtype(series)
            ):

                summary.update({
                    "mean": series.mean(),
                    "median": series.median(),
                    "std": series.std(),
                    "min": series.min(),
                    "max": series.max(),
                    "range": (
                        series.max() - series.min()
                    ),
                    "variance": series.var(),
                    "skew": series.skew(),
                })

            # -------------------------
            # Categorical / Text
            # -------------------------

            elif (
                pd.api.types.is_object_dtype(series)
                or pd.api.types.is_string_dtype(series)
                or pd.api.types.is_categorical_dtype(series)
            ):

                mode = series.mode()

                summary.update({
                    "mode": (
                        mode.iloc[0]
                        if not mode.empty
                        else None
                    ),
                    "mode_frequency": (
                        int(
                            (series == mode.iloc[0]).sum()
                        )
                        if not mode.empty
                        else 0
                    ),
                })

            # -------------------------
            # Datetime
            # -------------------------

            elif pd.api.types.is_datetime64_any_dtype(series):

                summary.update({
                    "min": series.min(),
                    "max": series.max(),
                    "range": (
                        series.max() - series.min()
                        if series.notna().any()
                        else None
                    ),
                })

            column_summary[column] = summary

        # ==========================================
        # Return complete dataset summary
        # ==========================================

        return {
            "rows": len(dataframe),

            "columns": len(dataframe.columns),

            "column_names": list(
                dataframe.columns
            ),

            "dtypes": dataframe.dtypes.to_dict(),

            "missing": dataframe.isnull().sum().to_dict(),

            "missing_total": int(
                dataframe.isnull().sum().sum()
            ),

            "duplicates": int(
                dataframe.duplicated().sum()
            ),

            "memory": int(
                dataframe.memory_usage(
                    deep=True
                ).sum()
            ),

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