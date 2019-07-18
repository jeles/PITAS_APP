import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from math import degrees

import ast
import pickle
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
#from sklearn.ensemble import RandomForestRegressor
#from sklearn.externals import joblib
#from sklearn.preprocessing import StandardScaler

## Import Data
df = pd.read_csv('prelim_dashboard_dataB.csv')
df.set_index('IntCode',inplace=True)
df.STlist=df.STlist.apply(lambda x: ast.literal_eval(x))

yearindex = list(range(2004,2018))
annuals = [1.83028721, 1.79206731, 1.85732815, 1.81908549, 1.8422619,
1.83685801, 1.92607393, 2., 1.93181818, 1.94909091, 1.86788814,
1.82018349, 1.88548242, 1.86012163]

with open('intconn.pkl', 'rb') as f:
    intconn = pickle.load(f)

names = list(intconn.keys())
nestedOptions = intconn[names[0]]

mqAPI = '378gIVg6jvZ20tjKV4oRB9QC4e1ddcoJ'
baseasset = r'https://www.mapquestapi.com/staticmap/v5/map'

bb = degrees(100/(6371.0*3280.84))

## Generate App

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [

        html.Div(children=[
            html.H1(children='Pittsburgh Intersection Threat Assessment System'),
            html.Div(children='''
                  Choose your intersection of interest:''')]),

        html.Div([
            html.Div([
            dcc.Dropdown(
                id='name-dropdown',
                options=[{'label':name, 'value':name} for name in names],
                value = 'FRIENDSHIP AVE'
                ),
                ],style={'width': '20%', 'display': 'inline-block'}),
            html.Div([
            dcc.Dropdown(
                id='opt-dropdown',
                value = 899
                ),
                ],style={'width': '20%', 'display': 'inline-block'})
            ], style={'borderBottom': 'thin lightgrey solid',
            'backgroundColor': 'rgb(250, 250, 250)', 'padding': '30px 30px'}  
        ),

        html.Div([dcc.Graph(id='x-time-series'),
            dcc.Graph(id='intmap')
        ],
        style={'columnCount': 2, 'display': 'inline-block', 'padding': '50 50'})
    ]
)

@app.callback(
    dash.dependencies.Output('opt-dropdown', 'options'),
    [dash.dependencies.Input('name-dropdown', 'value')]
)
def update_date_dropdown(name):
    return [{'label': i[0], 'value': i[1]} for i in intconn[name]]

def create_time_series(aot):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=yearindex,
            y=aot,
            name='Query Intersection',
            line_color='firebrick',
            mode='lines+markers'
        )
    )
    fig.add_trace(
        go.Scatter(
            x=yearindex,
            y=annuals,
            name='Average Intersection',
            line_color='royalblue',
            mode='lines+markers'
        )
    )
    fig['layout']['xaxis_title']='Year'
    fig['layout']['yaxis_title']='Number of Accidents'
    fig['layout']['title']=go.layout.Title(text="Accidents over time",x=0)
    fig['layout']['margin'] = {'l': 50, 'r': 50, 'b':50, 't': 50}

    return fig

def mapim(tind):
    tmplat = df.latitude[tind]
    tmplong = df.longitude[tind]
    bbox = [tmplat-bb,tmplat+bb,tmplong-bb,tmplong+bb]
    tmpstr = str(bbox[0])+','+str(bbox[2])+','+str(bbox[1])+','+str(bbox[3])
    assdata = {"key":mqAPI,"boundingBox":tmpstr,"zoom":'0',"type":"hyb","size":"512,512@2x"}
    testim = Image.open(BytesIO(requests.get(baseasset,assdata).content))
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=[tmplong],y=[tmplat])
        )
    fig.update_xaxes(range=bbox[2:4],showgrid=False)
    fig.update_yaxes(range=bbox[0:2],showgrid=False)
    fig['layout']['images']=[go.layout.Image(source=testim,
    xref='x',yref='y',x=bbox[2],y=bbox[1],sizex=bbox[3]-bbox[2],
    sizey=bbox[1]-bbox[0],sizing='stretch',layer='below')]
    fig['layout']['width']=512
    fig['layout']['height']=512
    fig['layout']['template']='plotly_white'
    fig['layout']['title']=go.layout.Title(text="Imagery of Intersection")
    #fig['layout']['margin'] = {'l': 20, 'r': 20, 'b':10, 't': 20}
    return fig

@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('opt-dropdown', 'value')])
def update_y_timeseries(tmpind):
    aot=ast.literal_eval(df.AccOverTime[tmpind])
    return create_time_series(aot)

@app.callback(
    dash.dependencies.Output('intmap', 'figure'),
    [dash.dependencies.Input('opt-dropdown', 'value')])
def update_im(tmpind):
    return mapim(tmpind)





if __name__ == '__main__':
    app.run_server()