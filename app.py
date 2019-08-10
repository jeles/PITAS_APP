import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from math import degrees

import ast
import numpy as np
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import base64
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

## Import Data
df = pd.read_csv('data/keymets.csv')
df.set_index('IntCode',inplace=True)

yearindex = list(range(2013,2018))
annuals = [1.94909091, 1.86788814,1.82018349, 1.88548242, 1.86012163]
bb = degrees(100/(6371.0*3280.84))

#Base inputs for the model
modins = pd.read_csv('data/modelinputs.csv')
modins.set_index('IntCode',inplace=True)
scaler = StandardScaler()
scalemodin = scaler.fit_transform(modins)

#Model import
model = pickle.load(open('data/RFmod20190726_f.sav', 'rb'))

#Sign information
signs = pd.read_csv('data/signlist.csv')

#Dictionary of intersections and street names
with open('data/intconn.pkl', 'rb') as f:
    intconn = pickle.load(f)

names = list(intconn.keys())
nestedOptions = intconn[names[0]]

#API information
mqAPI = '378gIVg6jvZ20tjKV4oRB9QC4e1ddcoJ'
baseasset = r'https://www.mapquestapi.com/staticmap/v5/map'


## Generate App


app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
server = app.server

app.layout = html.Div([

        html.Div([
            html.H1(children='Pittsburgh Intersection Threat Assessment System')],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"}),

        html.Div([

            html.H4(children='''
            Choose your intersection of interest:'''),

            html.Div([
            dcc.Dropdown(
                id='name-dropdown',
                options=[{'label':name, 'value':name} for name in names],
                value = 'FRIENDSHIP AVE'
                ),
                ],style={'width': '33%', 'display': 'inline-block','padding-right': '10px'}),
            html.Div([
            dcc.Dropdown(
                id='opt-dropdown',
                value = 899
                ),
                ],style={'width': '33%', 'display': 'inline-block','padding-left': '30px'})
            ], className='pretty_container eight columns',id='RoadSelect' 
        ),
        html.Div([
            html.Div([html.H3(children='Satellite Imagery of Intersection:'),dcc.Graph(id='intmap')],
            className='pretty_container four columns'),

            html.Div([html.H3(children='Accidents over Time:'),dcc.Graph(id='x-time-series')],
            className='pretty_container four columns')
        ],className='row flex-display'),
        
        html.Div([
            html.Div([
                html.H4(children='Actionable Safety Features: '),
                html.Label('Select a stop control method:'),
                dcc.Dropdown(
                    id='StopControlDrop',
                    options=[
                        {'label': 'Traffic Light', 'value': 'TL'},
                        {'label': 'Traffic Light with Flashing at night', 'value': 'TLF'},
                        {'label': 'Stop Sign Controlled', 'value': 'SS'},
                        {'label': 'None','value':'NO'}
                    ],
                    value='TLF'
                ),
                html.P('\nEnter mean speeds of the roads:'),
                dcc.Input(
                    id='meanspeed',
                    value='25'
                ),
                html.P('\nEnter the biggest difference in speeds for the roads:'),
                dcc.Input(
                    id='maxdiff',
                    value='0'
                ),
                html.P('\nToggle Safety Features:'),
                dcc.Checklist(
                    id ='togopts',
                    options=[
                        {'label': 'Restrict Turning', 'value': 'RT'},
                        {'label': 'Restrict Parking in Intersection', 'value': 'PARK'},
                        {'label': 'Add Intersection Warning Signs', 'value': 'WS'}
                    ],
                    value=['RT']
                )
            ],className='pretty_container four columns'),
            html.Div([html.H4(children='Predicted Mean Annual Accidents:'),html.Img(id='image1')],className='pretty_container four columns')

        ],className='row flex-display')

    ], id="mainContainer", style={"display": "flex", "flex-direction": "column"},
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
    #fig['layout']['title']=go.layout.Title(text="Accidents over time",x=0)
    #fig['layout']['width']=800
    #fig['layout']['height']=475
    fig['layout']['margin'] = {'l': 50, 'r': 50, 'b':50, 't': 50}

    return fig

def mapim(tind):
    tmplat = df.latitude[tind]
    tmplong = df.longitude[tind]

    #Generate image
    bbox = [tmplat-bb,tmplat+bb,tmplong-bb,tmplong+bb]
    tmpstr = str(bbox[0])+','+str(bbox[2])+','+str(bbox[1])+','+str(bbox[3])
    assdata = {"key":mqAPI,"boundingBox":tmpstr,"zoom":'0',"type":"hyb","size":"512,512@2x"}
    testim = Image.open(BytesIO(requests.get(baseasset,assdata).content))

    #Get relevant signs
    tmpsigns = signs[((signs.latitude>bbox[0])&(signs.latitude<bbox[1])&(signs.longitude>bbox[2])&(signs.longitude<bbox[3]))]

    fig = go.Figure()
    
    # Add int center
    fig.add_trace(
        go.Scatter(x=[tmplong], y=[tmplat],text='Interesection Center',
                mode='markers',marker=dict(color="rgb(255,255,255)",size=10,line=dict(color="rgb(0,0,0)",width=2)),name='Int Center')

    )   

    #Stops
    fig.add_trace(
        go.Scatter(x=tmpsigns.longitude[tmpsigns.stopsign==1], y=tmpsigns.latitude[tmpsigns.stopsign==1],text=tmpsigns.description[tmpsigns.stopsign==1],
                mode='markers',marker=dict(color="rgb(255,20,20)",size=10,line=dict(color="rgb(0,0,0)",width=2)),name='Stops')
    )

    #Traffic Light
    fig.add_trace(
        go.Scatter(x=tmpsigns.longitude[tmpsigns.light==1], y=tmpsigns.latitude[tmpsigns.light==1],text=tmpsigns.description[tmpsigns.light==1],
                mode='markers',marker=dict(color="rgb(250,250,10)",size=10,line=dict(color="rgb(0,0,0)",width=2)),name='Traffic Light')
    )

    #Turn restrictions
    fig.add_trace(
        go.Scatter(x=tmpsigns.longitude[tmpsigns.turnsign==1], y=tmpsigns.latitude[tmpsigns.turnsign==1],text=tmpsigns.description[tmpsigns.turnsign==1],
                mode='markers',marker=dict(color="rgb(20,250,250)",size=10,line=dict(color="rgb(0,0,0)",width=2)),name='Turn Restrict.')
    )

    #Yielding
    fig.add_trace(
        go.Scatter(x=tmpsigns.longitude[tmpsigns.yieldsign==1], y=tmpsigns.latitude[tmpsigns.yieldsign==1],text=tmpsigns.description[tmpsigns.yieldsign==1],
                mode='markers',marker=dict(color="rgb(250,100,20)",size=10,line=dict(color="rgb(0,0,0)",width=2)),name='Yield')
    )

    #Visibility
    fig.add_trace(
        go.Scatter(x=tmpsigns.longitude[tmpsigns.vissign==1], y=tmpsigns.latitude[tmpsigns.vissign==1],text=tmpsigns.description[tmpsigns.vissign==1],
                mode='markers',marker=dict(color="rgb(25,25,250)",size=10,line=dict(color="rgb(0,0,0)",width=2)),name='Yield')
    )

    fig.update_xaxes(range=bbox[2:4],showgrid=False)
    fig.update_yaxes(range=bbox[0:2],showgrid=False)
    fig['layout']['images']=[go.layout.Image(source=testim,
    xref='x',yref='y',x=bbox[2],y=bbox[1],sizex=bbox[3]-bbox[2],
    sizey=bbox[1]-bbox[0],sizing='stretch',layer='below')]
    #fig['layout']['width']=512
    #fig['layout']['height']=512
    fig['layout']['template']='plotly_white'
    #fig['layout']['title']=go.layout.Title(text="Imagery of Intersection")
    fig['layout']['margin'] = {'l': 50, 'r': 50, 'b':75, 't': 75}
    fig['layout']['yaxis']= {'scaleanchor': 'x', 'scaleratio': 1,'showgrid':False}
    return fig

@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('opt-dropdown', 'value')])
def update_y_timeseries(tmpind):
    aot=ast.literal_eval(df.AccOverTime[tmpind])[9:]
    return create_time_series(aot)

@app.callback(
    dash.dependencies.Output('intmap', 'figure'),
    [dash.dependencies.Input('opt-dropdown', 'value')])
def update_im(tmpind):
    return mapim(tmpind)

@app.callback(
    [dash.dependencies.Output('StopControlDrop', 'value'),
    dash.dependencies.Output('meanspeed','value'),
    dash.dependencies.Output('maxdiff','value'),
    dash.dependencies.Output('togopts','value')],
    [dash.dependencies.Input('opt-dropdown', 'value')]
)
def update_stopcont_dropdown(intnum):
    if (modins.TrafficLight.loc[intnum]==1)&(modins.TrafficFlash.loc[intnum]==0):
        stopcontout = 'TL'
    elif modins.TrafficFlash.loc[intnum]==1:
        stopcontout = 'TLF'
    elif modins.StopSign.loc[intnum]==1:
        stopcontout = 'SS'
    else:
        stopcontout = 'NO'
    chx =[]
    if  modins.turnrestriction.loc[intnum]>0:
        chx.append('RT')
    if modins.noparking.loc[intnum]>0:
        chx.append('PARK')
    if modins.vissigns.loc[intnum]>0:
        chx.append('WS')
    return [stopcontout, str(modins.meanspeed.loc[intnum]), str(modins.maxdiffspeed.loc[intnum]), chx]

@app.callback(
    dash.dependencies.Output('image1', 'src'),
    [dash.dependencies.Input('opt-dropdown', 'value'),
    dash.dependencies.Input('StopControlDrop','value'),
    dash.dependencies.Input('meanspeed','value'),
    dash.dependencies.Input('maxdiff','value'),
    dash.dependencies.Input('togopts','value')
    ])
def update_image_src(tmpind1,stopcont, mspe,mdiff,togoptions):
    #Alter stop control based on input 
    TI = modins.loc[tmpind1]
    if stopcont=='TL':
        TI.TrafficLight=1
        TI.TrafficFlash=0
        TI.StopSign=0
        TI.StopPerWay=0
    elif stopcont=='TLF':
        TI.TrafficLight=1
        TI.TrafficFlash=1
        TI.StopSign=0
        TI.StopPerWay=0
    elif stopcont=='SS':
        TI.TrafficLight=0
        TI.TrafficFlash=0
        TI.StopSign=1
        TI.StopPerWay=1
    elif stopcont=='NO':
        TI.TrafficLight=0
        TI.TrafficFlash=0
        TI.StopSign=0
        TI.StopPerWay=0
    #Alter the speeds based on input
    nmspe = []
    nmdiff = []
    try:
        nmspe = float(mspe)
    except:
        pass
    try: 
        nmdiff = float(mdiff)
    except:
        pass
    if nmspe:
        TI.meanspeed = nmspe
    if mdiff:
        TI.maxdiffspeed = nmdiff
    #Add in the sign options
    if 'RT' in togoptions:
        TI.turnrestriction=TI.numroad
    else:
        TI.turnrestriction=0
    if 'PARK' in togoptions:
        TI.noparking = TI.numroad
    else:
        TI.noparking = 0
    if 'WS' in togoptions:
        TI.vissigns = TI.numroad
    else:
        TI.vissigns = 0


    TI2 = scaler.transform(TI.values.reshape(1, -1))
    tmplev = int(model.predict(TI2.reshape(1, -1))[0])
    image_path = 'assets/Risk_Level_{}.png'.format(tmplev)
    encoded_image = base64.b64encode(open(image_path, 'rb').read())
    return 'data:image/png;base64,{}'.format(encoded_image.decode())



if __name__ == '__main__':
    app.run_server()