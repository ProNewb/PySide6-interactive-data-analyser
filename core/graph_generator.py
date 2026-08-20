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
        trendline=False,
        bell_curve=False
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
                title,
                trendline
            )

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
            return self.add_bell_curve(figure, dataframe, x_column, bell_curve)

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
            figure = self.create_area(
                dataframe,
                x_column,
                y_column,
                title
            )
            return self.add_trendline(figure, dataframe, x_column, y_column, trendline)

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
            figure = self.create_3d_chart(
                dataframe,
                x_column=x_column,
                y_column=y_column,
                z_column=z_column,
                title=title,
                color=color
            )
            return self.add_3d_fit(figure, dataframe, x_column, y_column, z_column, trendline)

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
        correlation = x_values[valid].corr(y_values[valid])
        figure.update_layout(
            annotations=[dict(
                text=f"Pearson r = {correlation:.3f}",
                x=0.02,
                y=0.98,
                xref="paper",
                yref="paper",
                showarrow=False
            )]
        )
        return figure

    def add_bell_curve(self, figure, dataframe, column, enabled):
        if not enabled or column is None:
            return figure
        values = pd.to_numeric(dataframe[column], errors="coerce").dropna()
        if len(values) < 2 or values.std() == 0:
            return figure
        x_values = np.linspace(values.min(), values.max(), 100)
        density = (
            np.exp(-0.5 * ((x_values - values.mean()) / values.std()) ** 2)
            / (values.std() * np.sqrt(2 * np.pi))
        )
        scale = len(values) * (values.max() - values.min()) / max(1, 20)
        figure.add_scatter(
            x=x_values,
            y=density * scale,
            mode="lines",
            name="Bell curve"
        )
        return figure

    def add_3d_fit(self, figure, dataframe, x, y, z, enabled):
        if not enabled or any(column is None for column in (x, y, z)):
            return figure
        values = dataframe[[x, y, z]].apply(
            pd.to_numeric,
            errors="coerce"
        ).dropna()
        if len(values) < 3:
            return figure
        matrix = np.column_stack([
            np.ones(len(values)), values[x], values[y]
        ]).astype(float)
        target = values[z].to_numpy(dtype=float)
        coefficients, _, _, _ = np.linalg.lstsq(
            matrix,
            target,
            rcond=None
        )
        x_grid = np.linspace(values[x].min(), values[x].max(), 20)
        y_grid = np.linspace(values[y].min(), values[y].max(), 20)
        x_mesh, y_mesh = np.meshgrid(x_grid, y_grid)
        z_mesh = coefficients[0] + coefficients[1] * x_mesh + coefficients[2] * y_mesh
        figure.add_surface(
            x=x_mesh,
            y=y_mesh,
            z=z_mesh,
            opacity=0.45,
            name="Best-fit plane"
        )
        return figure

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