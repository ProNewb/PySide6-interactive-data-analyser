


import plotly as px
class GraphGenerator:

    def create_graph(
        self,
        dataframe,
        graph_type,
        x_column,
        y_column,
        title=None
    ):

        pass




    def create_scatter(
        self,
        dataframe,
        x,
        y,
        title
    ):

        return px.scatter(
            dataframe,
            x=x,
            y=y,
            title=title
        )