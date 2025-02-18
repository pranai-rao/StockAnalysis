import dash
import yfinance as yf
import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input, dash_table
from datetime import datetime


def research():
    stocks = pd.read_csv('pages/sp500.csv')['Symbol'].to_list()
    df = pd.read_csv('pages/research.csv')
    if datetime.strptime(df['Last Updated'][0], '%Y-%m-%d').strftime('%Y-%m-%d') == datetime.today().strftime('%Y-%m-%d'):
        print("No updates necessary")
        return df

    valid_stock_names = []
    for ticker in stocks:
        ticker = str(ticker)
        if ticker.isalpha():
            valid_stock_names.append(ticker)

    df = yf.download(valid_stock_names, period='5d')[['Open', 'Close', 'Volume', 'High', 'Low']]

    ticker_list = []
    price_list = []
    day_change_list = []
    percent_day_change_list = []
    volume_list = []
    tip_list = []
    last_updated = []

    for ticker in valid_stock_names:
        if len(df['Close'][ticker]) < 2:
            print(ticker, "DENIED – Insufficient data")
            continue

        last_close = df['Close'][ticker].iloc[-1]
        previous_last_close = df['Close'][ticker].iloc[-2]

        if last_close >= 3:
            ticker_list.append(ticker)
            price_list.append(last_close)


            if pd.notna(previous_last_close) and pd.notna(last_close):
                day_change_list.append(round(last_close - previous_last_close, 2))
                percent_day_change_list.append(round((last_close - previous_last_close) / previous_last_close * 100, 2))
            else:
                day_change_list.append(None)
                percent_day_change_list.append(None)

            volume_list.append(df['Volume'][ticker].iloc[-1])

            std_dev = float(df['Close'][ticker].std())

            if (last_close - (float(df['High'][ticker].iloc[-2]) + float(df['Low'][ticker].iloc[-2])) / 2) / std_dev >= 0.75:
                tip_list.append('Wait')
            else:
                tip_list.append('Buy')

            last_updated.append(datetime.today().strftime('%Y-%m-%d'))
            print(ticker, "APPROVED")
        else:
            print(ticker, " = $" + str(last_close), "DENIED – Security price < $3")

        df = pd.DataFrame({'Ticker': ticker_list, 'Close': price_list, 'Day Change': day_change_list, 'Percent Change': percent_day_change_list, 'Tip': tip_list, 'Volume': volume_list, 'Last Updated': last_updated})
        df.to_csv('pages/research.csv', sep=',', index=False)
        return df


dash.register_page(__name__)

layout = [
    html.H1(children="Research", style={'textAlign': 'center'}),
    dash_table.DataTable(
        research().to_dict('records'),
        sort_action='native',
        sort_mode='multi',
        cell_selectable=False,
        style_data_conditional=[
            {
                'if' : {
                    'filter_query': '{Day Change} > 0',
                    'column_id' : 'Day Change',
                },
                'color' : '#38761d',
                'fontWeight': 'bold',
            },
            {
                'if' : {
                    'filter_query': '{Day Change} < 0',
                    'column_id' : 'Day Change',
                },
                'color' : '#990000',
                'fontWeight' : 'bold',
            },
            {
                'if': {
                    'filter_query': '{Percent Change} > 0',
                    'column_id': 'Percent Change',
                },
                'color': '#38761d',
                'fontWeight': 'bold',
            },
            {
                'if': {
                    'filter_query': '{Percent Change} < 0',
                    'column_id': 'Percent Change',
                },
                'color': '#990000',
                'fontWeight': 'bold',
            },
            {
                'if' : {
                    'filter_query' : '{Tip} contains "Buy"',
                    'column_id' : 'Tip',
                },
                'backgroundColor' : '#d9ead3'
            },
            {
                'if': {
                    'filter_query': '{Tip} contains "Wait"',
                    'column_id': 'Tip',
                },
                'backgroundColor': '#fff2cc'
            }
        ]
    )
]
