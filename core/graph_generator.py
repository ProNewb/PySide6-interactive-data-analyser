import plotly.express as px


class GraphGenerator:

    def create_graph(
        self,
        dataframe,
        graph_type,
        x_column=None,
        y_column=None,
        title=None
    ):

        if graph_type == "Scatter":
            return self.create_scatter(
                dataframe,
                x_column,
                y_column,
                title
            )

        elif graph_type == "Line":
            return self.create_line(
                dataframe,
                x_column,
                y_column,
                title
            )

        elif graph_type == "Bar":
            return self.create_bar(
                dataframe,
                x_column,
                y_column,
                title
            )

        elif graph_type == "Histogram":
            return self.create_histogram(
                dataframe,
                x_column,
                title
            )

        raise ValueError(
            f"Unsupported graph type: {graph_type}"
        )


    def create_scatter(
        self,
        dataframe,
        x,
        y,
        title=None
    ):

        return px.scatter(
            dataframe,
            x=x,
            y=y,
            title=title
        )


    def create_line(
        self,
        dataframe,
        x,
        y,
        title=None
    ):

        return px.line(
            dataframe,
            x=x,
            y=y,
            title=title
        )


    def create_bar(
        self,
        dataframe,
        x,
        y,
        title=None
    ):

        return px.bar(
            dataframe,
            x=x,
            y=y,
            title=title
        )


    def create_histogram(
        self,
        dataframe,
        x,
        title=None
    ):

        return px.histogram(
            dataframe,
            x=x,
            title=title
        )