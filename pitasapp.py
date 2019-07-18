import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

import re
import ast
import csv
#import requests
import pandas as pd
#from sklearn.ensemble import RandomForestRegressor
#from sklearn.externals import joblib
#from sklearn.preprocessing import StandardScaler

#get your necessary data
df = pd.read_csv('prelim_dashboard_dataB.csv')
df.set_index('IntCode',inplace=True)
df.STlist=df.STlist.apply(lambda x: ast.literal_eval(x))

with open('allstreets4.csv', 'r') as f:
    reader = csv.reader(f)
    streetlist = list(reader)[0]

yearindex = list(range(2004,2018))

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([
        dcc.Dropdown(id='input-1-state',options=[{'label':name, 'value':name} for name in streetlist],value='FRIENDSHIP AVE'),
        dcc.Dropdown(id='input-2-state',options=[{'label':name, 'value':name} for name in streetlist],value='S AIKEN AVE'),
        html.Button(id='submit-button', n_clicks=0, children='Submit'),
        html.Div(id='output-state')
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
        }
    ),

    html.Div([
        dcc.Graph(id='x-time-series')], 
        style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}
    )

])


def create_time_series(aot, title):
    return {
        'data': [go.Scatter(
            x=yearindex,
            y=aot,
            mode='lines+markers'
        )],
        'layout': {
            'height': 225,
            'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
            }],
            'yaxis': {'type': 'linear'},
            'xaxis': {'showgrid': False}
        }
    }

@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('submit-button','n_clicks')],
    [dash.dependencies.State('input-1-state', 'value'),
     dash.dependencies.State('input-2-state', 'value')])
def update_y_timeseries(n_clicks,road1,road2):
    tmpind = [x for x in df.index if (re.search(road1,df.STstr[x],re.IGNORECASE)) and (re.search(road2,df.STstr[x],re.IGNORECASE))]
    #tmpind = [9733]
    aot=ast.literal_eval(df.AccOverTime[tmpind[0]])
    title = '<b>{} and {}</b>'.format(road1,road2)
    return create_time_series(aot,title)

if __name__ == '__main__':
    app.run_server(debug=True)