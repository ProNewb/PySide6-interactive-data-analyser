class Aggregation:
    """Describe an aggregation operation to be performed on a DataFrame."""

    def __init__(self, group_by, aggregations):

        # Columns used to group the dataset.
        self.group_by = group_by

        # Aggregation operations to apply to the grouped data.
        self.aggregations = aggregations