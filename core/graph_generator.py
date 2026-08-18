import plotly.express as px


class GraphGenerator:
    '''Plotly graph generator class'''
    def create_graph(
        self,
        dataframe,
        graph_type,
        x_column=None,
        y_column=None,
        z_column=None,
        bins=None,
        size=None,
        title=None,
        color=None
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
                bins,
                title
            )

        elif graph_type == "Box":

            return self.create_box(
                dataframe,
                x_column,
                y_column,
                title
            )

        elif graph_type == "Pie":

            return self.create_pie(
                dataframe,
                x_column,
                y_column,
                title
            )

        elif graph_type == "Donut":

            return self.create_donut(
                dataframe,
                x_column,
                y_column,
                title
            )

        elif graph_type == "Area":

            return self.create_area(
                dataframe,
                x_column,
                y_column,
                title
            )

        elif graph_type == "Map":

            return self.create_map(
                dataframe,
                x_column,
                y_column,
                title
            )

        elif graph_type == "Tree Map":

            return self.create_tree_map(
                dataframe,
                x_column,
                y_column,
                title
            )

        elif graph_type == "Bubble":

            return self.create_bubble_chart(
                dataframe,
                x_column,
                y_column,
                size,
                title
            )

        elif graph_type == "3D Scatter":

            return self.create_3d_chart(
                dataframe,
                x_column=x_column,
                y_column=y_column,
                z_column=z_column,
                title=title,
                color=color
            )

        else:

            raise ValueError(
                f"Unsupported graph type: {graph_type}"
            )

    # --------------------------------------------------
    # Basic graphs
    # --------------------------------------------------

    def create_scatter(self, dataframe, x, y, title):

        return px.scatter(
            dataframe,
            x=x,
            y=y,
            title=title
        )

    def create_line(self, dataframe, x, y, title):

        return px.line(
            dataframe,
            x=x,
            y=y,
            title=title
        )

    def create_bar(self, dataframe, x, y, title):

        return px.bar(
            dataframe,
            x=x,
            y=y,
            title=title
        )

    # --------------------------------------------------
    # Statistical graphs
    # --------------------------------------------------

    def create_histogram(self, dataframe, x, bins, title):

        return px.histogram(
            dataframe,
            x=x,
            nbins=bins,
            title=title
        )

    def create_box(self, dataframe, x, y, title):

        return px.box(
            dataframe,
            x=x,
            y=y,
            title=title
        )

    # --------------------------------------------------
    # Proportional graphs
    # --------------------------------------------------

    def create_pie(self, dataframe, names, values, title):

        return px.pie(
            dataframe,
            names=names,
            values=values,
            title=title
        )

    def create_donut(self, dataframe, names, values, title):

        return px.pie(
            dataframe,
            names=names,
            values=values,
            hole=0.45,
            title=title
        )

    # --------------------------------------------------
    # Relationship / trend graphs
    # --------------------------------------------------

    def create_area(self, dataframe, x, y, title):

        return px.area(
            dataframe,
            x=x,
            y=y,
            title=title
        )

    def create_bubble_chart(self, dataframe, x, y, size, title):

        return px.scatter(
            dataframe,
            x=x,
            y=y,
            size=size,
            title=title
        )

    # --------------------------------------------------
    # Hierarchical graph
    # --------------------------------------------------

    def create_tree_map(self, dataframe, names, values, title):

        return px.treemap(
            dataframe,
            path=[names],
            values=values,
            title=title
        )

    # --------------------------------------------------
    # Geographic graph
    # --------------------------------------------------

    def create_map(self, dataframe, latitude, longitude, title):

        return px.scatter_map(
            dataframe,
            lat=latitude,
            lon=longitude,
            title=title
        )

    # -------------------------------------------------------
    # 3D
    #---------------------------------------------------------

    def create_3d_chart(self,dataframe,x_column,y_column,z_column,color,title):
            
        return px.scatter_3d(
            dataframe,
            x=x_column,
            y=y_column,
            z=z_column,

            title=title,
            color=color
        )