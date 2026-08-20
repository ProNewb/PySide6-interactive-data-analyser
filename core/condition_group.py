class ConditionGroup:
    """Represent multiple filter conditions combined with AND or OR."""

    def __init__(self, conditions, logic="AND"):

        # Conditions that make up this group.
        self.conditions = conditions

        # Logical operator used to combine the conditions.
        self.logic = logic

    def evaluate(self, dataframe):
        """
        Evaluate all conditions against a DataFrame.

        Returns a pandas boolean Series indicating which rows
        satisfy the condition group.
        """

        # An empty condition group matches every row.
        if not self.conditions:

            return dataframe.index.to_series().map(
                lambda _: True
            )

        # Evaluate each individual condition.
        results = [
            condition.evaluate(dataframe)
            for condition in self.conditions
        ]

        # Combine conditions using logical AND.
        if self.logic == "AND":

            result = results[0]

            for condition_result in results[1:]:

                result = (
                    result &
                    condition_result
                )

            return result

        # Combine conditions using logical OR.
        if self.logic == "OR":

            result = results[0]

            for condition_result in results[1:]:

                result = (
                    result |
                    condition_result
                )

            return result

        raise ValueError(
            f"Unknown logic operator: {self.logic}"
        )

    def describe(self):
        return f" {self.logic} ".join(
            condition.describe()
            for condition in self.conditions
        )