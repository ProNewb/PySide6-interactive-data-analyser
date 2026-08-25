class Aggregation:
    """Describe an aggregation operation to be performed on a DataFrame."""

    def __init__(self, group_by, aggregations):

        # Columns used to group the dataset.
        self.group_by = group_by

        # Aggregation operations to apply to the grouped data.
        self.aggregations = aggregations

    def describe(self):
        groups = ", ".join(str(column) for column in self.group_by)
        operations = ", ".join(
            f"{function}({column})"
            for column, function in self.aggregations
        )
        return f"group by {groups}; {operations}"