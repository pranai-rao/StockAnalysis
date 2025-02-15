# Read stocks
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input
from datetime import datetime
from dateutil.relativedelta import relativedelta

stocks = pd.read_csv('stock_list.csv')
app = Dash()

app.layout = [
    html.H1(children='Stock Analysis', style={'textAlign':'center'}),
    dcc.Dropdown(stocks.Symbol.unique(), 'AAPL', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
]

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    df = yf.Ticker(value).history(start='2024-02-01')[['Open', 'Close', 'Volume', 'High', 'Low']]

    # Getting the bollinger values
    df['BM'] = df['Close'].rolling(window=20).mean()
    df['SD'] = df['Close'].rolling(window=20).std()
    df['BU'] = df['BM'] + 2 * df['SD']
    df['BL'] = df['BM'] - 2 * df['SD']

    # Create a Date column
    df['Date'] = df.index
    # Drop the Date as index
    df.reset_index(drop=True, inplace=True)
    df.head(5)

    fig = go.Figure(layout=go.Layout(template='plotly_white', title=value + " – " + stocks[stocks['Symbol'] == value]['Company'].values[0], height=500, legend_title='Legend'))

    fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], showlegend=False))
    # fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Price', line=dict(color='#79bc77')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['BU'], mode='lines', name='Upper', line=dict(color='#9999ff')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['BM'], mode='lines', name='SMA', line=dict(color='#000000')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['BL'], mode='lines', name='Lower', line=dict(color='#9999ff')))

    fig.update_yaxes(title_text='Price')
    fig.update_xaxes(title_text='Date')

    set_padding(fig)

    # Remove dates without values
    fig.update_xaxes(rangebreaks=[dict(values=[d for d in pd.date_range(start=df.index[0],end=df.index[-1]).strftime("%Y-%m-%d").tolist() if not d in [d.strftime("%Y-%m-%d") for d in pd.to_datetime(df.index)]])])

    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=3,
                         label="3m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date",
            range=[(datetime.today() - relativedelta(months=6)).strftime('%Y-%m-%d'), datetime.today().strftime('%Y-%m-%d')]
        )
    )

    return fig


def set_padding(fig):
    fig.update_layout(margin=go.layout.Margin(r=10, b=10)) # right, bottom margin


if __name__ == '__main__':
    app.run(debug=True)
