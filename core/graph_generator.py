import plotly.express as px
import numpy as np
import pandas as pd


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
        color=None,
        trendline=False
    ):

        if graph_type == "Scatter":
            figure = self.create_scatter(
                dataframe,
                x_column,
                y_column,
                title
            )
            return self.add_trendline(figure, dataframe, x_column, y_column, trendline)

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

            figure = self.create_bubble_chart(
                dataframe,
                x_column,
                y_column,
                size,
                title
            )
            return self.add_trendline(figure, dataframe, x_column, y_column, trendline)

        elif graph_type == "Heatmap":
            return self.create_heatmap(dataframe, title)

        elif graph_type == "Correlation Map":
            return self.create_correlation_map(dataframe, title)

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

    def add_trendline(self, figure, dataframe, x, y, enabled):
        if not enabled or x is None or y is None:
            return figure
        numeric = dataframe[[x, y]].dropna()
        if len(numeric) < 2:
            return figure
        x_values = pd.to_numeric(numeric[x], errors="coerce")
        y_values = pd.to_numeric(numeric[y], errors="coerce")
        valid = ~(x_values.isna() | y_values.isna())
        if valid.sum() < 2:
            return figure
        coefficients = np.polyfit(x_values[valid], y_values[valid], 1)
        ordered = np.sort(x_values[valid])
        figure.add_scatter(
            x=ordered,
            y=np.polyval(coefficients, ordered),
            mode="lines",
            name="Trend line"
        )
        return figure

    def create_heatmap(self, dataframe, title):
        numeric = dataframe.select_dtypes(include="number")
        return px.imshow(
            numeric.corr(),
            text_auto=True,
            title=title or "Numeric heatmap",
            color_continuous_scale="RdBu_r"
        )

    def create_correlation_map(self, dataframe, title):
        return self.create_heatmap(
            dataframe,
            title or "Correlation map"
        )