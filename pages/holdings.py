import dash
import yfinance as yf
import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input, dash_table
from dateutil.relativedelta import relativedelta
from datetime import datetime
dash.register_page(__name__)


# To add a stock, add the first three details in the CSV followed by 6 commas, and update the first 'Last Updated' to some time in the past
def update_data():
    df = pd.read_csv('pages/purchase_list.csv')
    if datetime.strptime(df['Last Updated'][0], '%Y-%m-%d').strftime('%Y-%m-%d') == datetime.today().strftime('%Y-%m-%d'):
        print("No updates necessary")
        return df
    price = []
    volume = []
    analyst = []
    profit = []
    percent_profit = []
    last_update = []

    for i, ticker in enumerate(df['Ticker']):
        info = yf.Ticker(ticker).info
        if info['marketState'] == 'CLOSED':
            current_price = info['regularMarketPrice']
        else:
            current_price = info['previousClose']

        price.append(round(current_price, 2))
        purchase_price = df['Purchase Price'].iloc[i]

        if pd.notna(purchase_price) and pd.notna(current_price):
            profit.append(round((current_price - purchase_price) * df['Shares'].iloc[i], 2))
            percent_profit.append(round((current_price - purchase_price) / purchase_price * 100, 2))
        else:
            profit.append(None)  # or use None if you prefer
            percent_profit.append(None)

        volume.append(info.get('volume', None))
        analyst.append(info.get('averageAnalystRating', None))
        last_update.append(datetime.today().strftime('%Y-%m-%d'))

    df['Price'] = price
    df['Volume'] = volume
    df['Profit'] = profit
    df['Percent Profit'] = percent_profit
    df['Analyst Rating'] = analyst
    df['Last Updated'] = last_update

    df.to_csv('pages/purchase_list.csv', sep=',', index=False, na_rep='NaN')
    return df


layout = [
    html.H1(children="Account Holdings", style={'textAlign': 'center'}),
    dash_table.DataTable(
        update_data().to_dict('records'),
        sort_action='native',
        sort_mode='multi',
        style_data_conditional=[
            {
                'if' : {
                    'filter_query': '{Profit} > 0',
                    'column_id' : 'Profit',
                },
                'color' : '#38761d',
                'fontWeight': 'bold',
            },
            {
                'if' : {
                    'filter_query': '{Profit} < 0',
                    'column_id' : 'Profit',
                },
                'color' : '#990000',
                'fontWeight' : 'bold',
            },
            {
                'if': {
                    'filter_query': '{Percent Profit} > 0',
                    'column_id': 'Percent Profit',
                },
                'color': '#38761d',
                'fontWeight': 'bold',
            },
            {
                'if': {
                    'filter_query': '{Percent Profit} < 0',
                    'column_id': 'Percent Profit',
                },
                'color': '#990000',
                'fontWeight': 'bold',
            },
            {
                'if' : {
                    'filter_query' : '{Analyst Rating} contains "Buy"',
                    'column_id' : 'Analyst Rating',
                },
                'backgroundColor' : '#d9ead3'
            },
            {
                'if': {
                    'filter_query': '{Analyst Rating} contains "Hold"',
                    'column_id': 'Analyst Rating',
                },
                'backgroundColor': '#fff2cc'
            },
            {
                'if': {
                    'filter_query': '{Analyst Rating} contains "Sell"',
                    'column_id': 'Analyst Rating',
                },
                'backgroundColor': '#f4cccc'
            }
        ]
    )
]

