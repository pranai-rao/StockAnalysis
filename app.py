# Read stocks
import dash
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input
from datetime import datetime
from dateutil.relativedelta import relativedelta

stocks = pd.read_csv('stock_list.csv')

app = Dash()
server = app.server

app.layout = [
    html.H1(children='Stock Analysis', style={'textAlign':'center'}),
    dcc.Dropdown(stocks.Symbol.unique(), 'AAPL', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
]

@callback(
    Output('graph-content', 'figure'),
    [Input('dropdown-selection', 'value'),
     Input('graph-content', 'relayoutData')]
)
def update_graph(value, relayoutData):
    # Fetch 2+ years of data to support the "All" selector
    df = yf.Ticker(value).history(period="5y")[['Open', 'Close', 'Volume', 'High', 'Low']]

    # Compute Bollinger Bands
    df['BM'] = df['Close'].rolling(window=20).mean()
    df['SD'] = df['Close'].rolling(window=20).std()
    df['BU'] = df['BM'] + 2 * df['SD']
    df['BL'] = df['BM'] - 2 * df['SD']

    # Convert index to column
    df['Date'] = df.index
    df.reset_index(drop=True, inplace=True)

    # Create figure
    fig = go.Figure(layout=go.Layout(template='plotly_white', title=value, height=500))

    fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], showlegend=False))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['BU'], mode='lines', name='Upper Band', line=dict(color='#9999ff')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['BM'], mode='lines', name='SMA', line=dict(color='#000000')))  #, visible='legendonly'))  # Can be toggled in legend
    fig.add_trace(go.Scatter(x=df['Date'], y=df['BL'], mode='lines', name='Lower Band', line=dict(color='#9999ff')))

    # Handle x-axis range correctly
    if relayoutData and ('xaxis.range' in relayoutData or 'xaxis.range[0]' in relayoutData):
        x_start, x_end = relayoutData.get('xaxis.range', [None, None])
        if x_start is None or x_end is None:
            x_start = relayoutData.get('xaxis.range[0]', df['Date'].min())
            x_end = relayoutData.get('xaxis.range[1]', df['Date'].max())
    else:
        # Default **only on first load** (not on button clicks)
        x_end = df['Date'].max()
        x_start = x_end - relativedelta(months=6)

    # Ensure x_start and x_end are strings for comparison
    x_start, x_end = str(x_start), str(x_end)

    # Filter data based on x-axis range
    filtered_df = df[(df['Date'] >= x_start) & (df['Date'] <= x_end)]

    # Adjust y-axis range based on Bollinger Bands
    if not filtered_df.empty:
        y_min = filtered_df['BL'].min() - 5
        y_max = filtered_df['BU'].max() + 5
        fig.update_yaxes(range=[y_min, y_max])

    # Set correct x-axis range
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(count=5, label="5y", step="year", stepmode="backward")  # This should now properly extend to all available data
                ])
            ),
            rangeslider=dict(visible=True),
            type="date",
            range=[x_start, x_end]  # Dynamically adjust based on selection
        )
    )

    return fig


def set_padding(fig):
    fig.update_layout(margin=go.layout.Margin(r=10)) # right, bottom margin


if __name__ == '__main__':
    app.run(debug=True)

