import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go 

class CurveGenerator:
       
    def add_trendline(self, figure, dataframe, x, y):

        data = dataframe[[x, y]].copy()
        data = data.loc[:, ~data.columns.duplicated()]

        data[x] = pd.to_numeric(data[x], errors="coerce")
        data[y] = pd.to_numeric(data[y], errors="coerce")
        data = data.dropna()

        if len(data) < 2:
            return figure, None

        X = data[[x]].to_numpy()
        Y = data[y].to_numpy()

        model = LinearRegression()
        model.fit(X, Y)

        xs = np.linspace(X.min(), X.max(), 200).reshape(-1, 1)
        ys = model.predict(xs)

        figure.add_trace(
            go.Scatter(
                x=xs.flatten(),
                y=ys,
                mode="lines",
                name="Best fit",
                line=dict(color="red", dash="dash")
            )
        )

        return figure, model


    def add_regression_plane(self, figure, dataframe, x, y, z):

        data = dataframe[[x, y, z]].apply(
            pd.to_numeric,
            errors="coerce"
        ).dropna()

        if len(data) < 4:
            return figure, None

        X = data[[x, y]].to_numpy()
        Z = data[z].to_numpy()

        model = LinearRegression()
        model.fit(X, Z)

        padding_x = (data[x].max() - data[x].min()) * 0.02
        padding_y = (data[y].max() - data[y].min()) * 0.02

        xs = np.linspace(
            data[x].min() - padding_x,
            data[x].max() + padding_x,
            25
        )

        ys = np.linspace(
            data[y].min() - padding_y,
            data[y].max() + padding_y,
            25
        )

        xx, yy = np.meshgrid(xs, ys)

        zz = model.predict(
            np.column_stack([
                xx.ravel(),
                yy.ravel()
            ])
        ).reshape(xx.shape)

        figure.add_trace(
            go.Surface(
                x=xx,
                y=yy,
                z=zz,
                opacity=0.45,
                showscale=False,
                name="Regression plane"
            )
        )

        return figure, model


    def add_bell_curve(
        self,
        figure,
        dataframe,
        column,
        bins,
        enabled
    ):
        if not enabled:
            return figure

        values = (
            pd.to_numeric(dataframe[column], errors="coerce")
            .dropna()
        )

        if len(values) < 2:
            return figure

        μ = values.mean()
        σ = values.std()

        x = np.linspace(values.min(), values.max(), 300)

        pdf = (
            np.exp(-0.5 * ((x - μ) / σ) ** 2)
            / (σ * np.sqrt(2 * np.pi))
        )

        bin_width = (values.max() - values.min()) / bins

        y = pdf * len(values) * bin_width

        figure.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                name="Normal distribution",
                line=dict(width=3)
            )
        )

        return figure
