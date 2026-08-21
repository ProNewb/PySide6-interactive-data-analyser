import plotly.express as px
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go

from ui.helpers.curve_generator import CurveGenerator 

class GraphGenerator:
    '''Plotly graph generator class'''
    def __init__(self):
        self.curves = CurveGenerator()
    
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
        trendline=False,
        bell_curve=False
    ):

        if graph_type == "Scatter":

            figure = self.create_scatter(dataframe, x_column, y_column, title)

            if trendline:
                figure, _ = self.curves.add_trendline(
                    figure,
                    dataframe,
                    x_column,
                    y_column
                )

            return figure

        if graph_type == "Line":

            figure = self.create_line(
                dataframe,
                x_column,
                y_column,
                title,
                curve=False
            )

            if trendline:
                figure, _ = self.curves.add_trendline(
                    figure,
                    dataframe,
                    x_column,
                    y_column
                )

            return figure

        elif graph_type == "Bar":

            return self.create_bar(
                dataframe,
                x_column,
                y_column,
                title
            )

        elif graph_type == "Histogram":
            figure = self.create_histogram(
                dataframe,
                x_column,
                bins,
                title
            )
            return self.curves.add_bell_curve(figure, dataframe, x_column,bins, bell_curve)

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

        if graph_type == "Area":

            figure = self.create_area(dataframe, x_column, y_column, title)

            if trendline:
                figure, _ = self.curves.add_trendline(
                    figure,
                    dataframe,
                    x_column,
                    y_column
                )

            return figure

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
                z_column,
                title
            )

            if trendline:
                figure, _ = self.curves.add_trendline(
                    figure,
                    dataframe,
                    x_column,
                    y_column
                )

            return figure

        elif graph_type == "Heatmap":
            return self.create_heatmap(dataframe, title)

        elif graph_type == "Correlation Map":
            return self.create_correlation_map(dataframe, title)

        elif graph_type == "3D Scatter":
            figure = self.create_3d_chart(
                dataframe,
                x_column=x_column,
                y_column=y_column,
                z_column=z_column,
                title=title,
                color=color
            )
            if trendline:
                figure, model = self.curves.add_regression_plane(
                    figure,
                    dataframe,
                    x_column,
                    y_column,
                    z_column
                )

            return figure
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

    def create_line(self, dataframe, x, y, title, curve=False):

        figure = px.line(
            dataframe,
            x=x,
            y=y,
            title=title
        )
        if curve:
            for trace in figure.data:
                trace.line.shape = "spline"
        return figure

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




    def create_heatmap(self, dataframe, title):
        numeric = dataframe.select_dtypes(include="number")
        return px.imshow(
            numeric.T,
            text_auto=True,
            title=title or "Numeric value heatmap",
            color_continuous_scale="RdBu_r"
        )

    def create_correlation_map(self, dataframe, title):
        numeric = dataframe.select_dtypes(include="number")
        return px.imshow(
            numeric.corr(),
            text_auto=True,
            title=title or "Pearson correlation map",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1
        )

    def generate_prediction_curve(self):

        feature = self.prediction_feature.currentData()

        numeric = self.dataframe.select_dtypes("number")

        values = np.linspace(
            numeric[feature].min(),
            numeric[feature].max(),
            self.prediction_points.value()
        )

        sample = {}

        for col in self.selected_features():

            if col == feature:
                sample[col] = values

            elif pd.api.types.is_numeric_dtype(self.dataframe[col]):

                sample[col] = [self.dataframe[col].median()] * len(values)

            else:

                sample[col] = [self.dataframe[col].mode()[0]] * len(values)

        predict_df = pd.DataFrame(sample)

        y = self.pipeline.predict(predict_df)

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=values,
                y=y,
                mode="lines",
                name="Prediction"
            )
        )

        self.prediction_graph.display_graph(fig)