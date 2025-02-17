import dash
import yfinance as yf
import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input, dash_table
from dateutil.relativedelta import relativedelta

dash.register_page(__name__)

layout = [
    html.H1(children="Research", style={'textAlign': 'center'})
]
