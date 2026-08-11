class Aggregation:

    def __init__(
        self,
        group_by,
        aggregations
    ):

        self.group_by = group_by
        self.aggregations = aggregations