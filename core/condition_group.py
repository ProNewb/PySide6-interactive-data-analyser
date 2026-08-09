class ConditionGroup:

    def __init__(self, conditions, logic="AND"):

        self.conditions = conditions
        self.logic = logic

    def evaluate(self, dataframe):

        if not self.conditions:
            return dataframe.index.to_series().map(lambda x: True)

        results = [
            condition.evaluate(dataframe)
            for condition in self.conditions
        ]

        if self.logic == "AND":

            result = results[0]

            for condition_result in results[1:]:
                result = result & condition_result

            return result

        elif self.logic == "OR":

            result = results[0]

            for condition_result in results[1:]:
                result = result | condition_result

            return result

        raise ValueError(
            f"Unknown logic operator: {self.logic}"
        )