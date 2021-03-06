# https://www.statworx.com/en/blog/how-to-build-a-dashboard-in-python-plotly-dash-step-by-step-tutorial/#data
import datetime
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output

import yfinance as yf

# get historical data
start = datetime.datetime(2020, 1, 1)
end = datetime.datetime.now()

tickerSymbols = ["VOO", "MSFT", "ARKK","VTI", "BAH", "VFINX"]

first_ticker = True
for ticker in tickerSymbols:
    tickerData = yf.Ticker(ticker)
    tickerDf = tickerData.history(period='1d', start=start, end=end)
    # add stock symbol as a column value
    tickerDf.insert(0,"stock", ticker)
    if first_ticker:
        tickerDf.to_csv("data/mystocks.csv", mode='w')
        first_ticker = False
    else:
        # append and skip headers after first item
        tickerDf.to_csv("data/mystocks.csv", mode='a', header=False)


# Load data for plotting graphs
df = pd.read_csv('data/mystocks.csv', index_col=0, parse_dates=True)

#  PLOTY CODE
# Initialize the app
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

def get_options(list_stocks):
    dict_list = []
    for i in list_stocks:
        dict_list.append({'label': i, 'value': i})

    return dict_list

# USING CUSTOM CSS - https://github.com/plotly/dash-recipes/blob/master/dash-local-css-link.py
app.layout = html.Div(
    children=[html.Link(
        rel='stylesheet',
        href='/assets/style.css'
    ),
        html.Div(className='row',
                 children=[
                    html.Div(className='four columns div-user-controls',
                             children=[
                                 html.H2('DASH - STOCK PRICES'),
                                 html.P('Visualising time series with Plotly - Dash.'),
                                 html.P('Pick one or more stocks from the dropdown below.'),
                                 html.Div(
                                     className='div-for-dropdown',
                                     children=[
                                         dcc.Dropdown(id='stockselector', options=get_options(df['stock'].unique()),
                                                      multi=True, value=[df['stock'].sort_values()[0]],
                                                      style={'backgroundColor': '#1E1E1E'},
                                                      className='stockselector'
                                                      )
                                     ],

                                     style={'color': '#1E1E1E'})
                                ]
                             ),
                    html.Div(className='eight columns div-for-charts bg-grey',
                             children=[
                                 dcc.Graph(id='timeseries', config={'displayModeBar': False}, animate=True),
                                 html.Div([
                                     generate_table(df[df['stock'] == 'BAH'].tail()),
                                 ], style={'color': 'white', 'padding': '50px'})
                             ]),
                              ])
        ]

)


# Callback for timeseries price
@app.callback(Output('timeseries', 'figure'),
              [Input('stockselector', 'value')])
def update_graph(selected_dropdown_value):
    trace1 = []
    df_sub = df
    for stock in selected_dropdown_value:
        trace1.append(go.Scatter(x=df_sub[df_sub['stock'] == stock].index,
                                 y=df_sub[df_sub['stock'] == stock]['Close'],
                                 mode='lines',
                                 opacity=0.7,
                                 name=stock,
                                 textposition='bottom center'))
    traces = [trace1]
    data = [val for sublist in traces for val in sublist]
    figure = {'data': data,
              'layout': go.Layout(
                  colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  title={'text': 'Stock Prices', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [df_sub.index.min(), df_sub.index.max()]},
              ),

              }

    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
