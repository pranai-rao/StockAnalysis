# Read stocks
import dash
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input
from dateutil.relativedelta import relativedelta

app = Dash(__name__, use_pages=True)
server = app.server

app.layout = html.Div(
    [
        html.Div("Stock Analysis", style={'fontSize':50, 'textalign':'center'}),
        html.Div([
            dcc.Link(page['name']+"  |  ", href=page['path'])
            for page in dash.page_registry.values()
        ]),
        html.Hr(),
        dash.page_container
    ]
)

if __name__ == "__main__":
    app.run(debug=True)

