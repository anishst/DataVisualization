import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd

df = pd.read_excel('data/Payments.xlsx', sheet_name="Payments")

print(df.head())

# https://dash.plotly.com/layout
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

fig = px.bar(df.head(2), x="Category", y="Amount", color="Category", barmode="group")

app = dash.Dash()
app.layout = html.Div([
    html.Div(id="my-div"),
    generate_table(df),
    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])




if __name__ == '__main__':
    app.run_server()
