#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 00:08:22 2021

@author: anja
"""

from scraper import *
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from plotly.offline import plot
import plotly.graph_objects as go
import pandas as pd
#get some data to play with

river_stats=get_river_stats('isar','garmisch-o-d-partnachmuendung-16401006',365)
#Note: that site gives me 13 months of data.
#use plotly to plot the data and color it according to the enjoyment level
# of kayaking = too low water, just enough, perfect, high, too high
# have another one where you analyze according to the day of the weeks or weekends or
# according to the months=get statistics how many paddelable days there were.

#make a new column with categorical labels too low, low, perfect, high, too high
def make_categ_waterlevels(river_stats,at_least=90,low=100,medium=120,high=170):
    river_stats['level_cat']=pd.cut(river_stats.waterlevel,
               bins=[0,at_least,low,medium,high,high*10000],include_lowest=True,
               right=True,
               labels=['too low','low','medium','high','too high'])
    return river_stats


lcat=['too low','low','medium','high','too high']

river_stats=make_categ_waterlevels(river_stats,90,100,120,170)

'''
fig = px.line(river_stats, x="datetime", y="waterlevel", title='Waterlevel evolution')
fig.add_trace(go.Scatter(x=river_stats[river_stats.level_cat=='medium'].datetime,
                         y=river_stats[river_stats.level_cat=='medium'].waterlevel,
                         mode='markers'))
plot(fig)
'''

app=dash.Dash(__name__)

app.layout=html.Div(#[
        children=[html.H1(children='River Level Stats'),
        dcc.Input(
            id="input_url",
            type="url",
            placeholder="https://www.hnd.bayern.de/pegel/isar/garmisch-o-d-partnachmuendung-16401006/tabelle?methode=wasserstand&days=50"
            ),
        dcc.Checklist(
                id="checklist",
                options=[{'label':x,'value':x}
                for x in lcat],
                value=lcat[:],
                labelStyle={'display': 'inline-block'}
                ),
        dcc.Graph(id='line-chart'),
        # dcc.Store inside the app that stores the intermediate value
        dcc.Store(id='intermediate-value')
        ])

@app.callback(
        Output('line-chart','figure'),
        [Input('checklist','value'),
         Input('intermediate-value','data')])
def update_line_chart(river_level,jsonified_data):
    '''
    update the figure when the user changes which river levels to look at
    '''
    river_stats=pd.read_json(jsonified_data, orient='split')
    print('want to show ',river_level, ' river level')
    fig = px.line(river_stats, x="datetime", y="waterlevel", 
                  title='Waterlevel evolution')
    mask =river_stats.level_cat.isin(river_level)
    fig.add_trace(go.Scatter(x=river_stats[mask].datetime,
                         y=river_stats[mask].waterlevel,
                         mode='markers'))
    return fig


@app.callback(
        Output('intermediate-value', 'data'),
        [Input('input_url','value')])
def update_placeholder(url):
    '''
    load new data!
    '''
    #try to load the url two times
    try:
        river_st=get_river_stats_url(url)
    except URLError:
        try:
            river_st=get_river_stats_url(url)
        except URLError:
            print("wrong url...")
    river_st=make_categ_waterlevels(river_st)
    return river_st.to_json(date_format='iso', orient='split')
    

app.run_server(debug=True)













