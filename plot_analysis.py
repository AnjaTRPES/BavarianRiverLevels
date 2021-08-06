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
import urllib.error
import pandas as pd
import pickle
from datetime import date
from dateutil.relativedelta import relativedelta


#get the dictionairy
with open('river_stats.json', 'rb') as fp:
    river_stats_dict= pickle.load(fp)

#get the river stats of the Loisach
river_stats=get_river_stats_url_days(river_stats_dict['Loisach']["url"],365)


lcat=['too low','low','medium','high','too high']
lcat_colors=['black','blue','green','orange','red']
lcat_colors_dict=dict(zip(lcat,lcat_colors))

river_stats=make_categ_waterlevels(river_stats,
                                   river_stats_dict['Loisach']["levels"]["at_least"],
                                   river_stats_dict['Loisach']["levels"]["low"],
                                   river_stats_dict['Loisach']["levels"]["medium"],
                                   river_stats_dict['Loisach']["levels"]["high"]
                                   )

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
                  dcc.Markdown('The easy way to decide whether a river has good levels for kayaking!'),
                  html.Div([
                  dcc.Dropdown(                                                 
                          id='which_river',
                          options=[dict([(i, key) for i in ['label','value']]) for key in list(river_stats_dict.keys())],
                          value=list(river_stats_dict.keys())[0]
                        ),
                  html.Label("Days: "),
                  dcc.Input(
                          id='number_days',
                          type='number',
                          placeholder=364,
                          value=364,
                          )
                  ],style={'columnCount':3}),
                  dcc.Checklist(
                          id='Show_hidden',
                          options=[{'label':'custom values','value':'Show'}],
                          labelStyle={'display': 'inline-block'}),
                  #Create a div where the user can put in a html to load, and custom set the levels
                  html.Div([
                          html.Label('url'),
                          dcc.Input(
                                id="input_url",
                                type="url",
                                value=river_stats_dict['Loisach']["url"],
                                ),
                         html.Label('at_least'),
                         dcc.Input(
                                 id='at_least',
                                 type='number',
                                 value=river_stats_dict['Loisach']["levels"]["at_least"]),
                         html.Label('low'),
                         dcc.Input(
                                 id='low',
                                 type='number',
                                 value=river_stats_dict['Loisach']["levels"]["low"]),
                        html.Label('medium'),
                         dcc.Input(
                                 id='medium',
                                 type='number',
                                 value=river_stats_dict['Loisach']["levels"]["medium"]),
                        html.Label('at_least'),
                         dcc.Input(
                                 id='high',
                                 type='number',
                                 value=river_stats_dict['Loisach']["levels"]["high"])
                        
                          ], id='show_custom', style={'display':'none'}),        
        dcc.Checklist(
                id="checklist",
                options=[{'label':x,'value':x}
                for x in lcat],
                value=lcat[:],
                labelStyle={'display': 'inline-block'}
                ),
        dcc.Graph(id='line-chart'),
        
        html.H1(children='Look at some statistics'),
        html.Div([
            html.Div(
                [    dcc.DatePickerRange(
                        id='my-date-picker-range',
                        min_date_allowed=date.today()-relativedelta(months=13),
                        max_date_allowed=date.today(),
                        start_date=date.today()-relativedelta(months=13),
                        end_date=date.today()
                    ),]),
                html.Label('Water level/day'),
                dcc.Dropdown(                                                 
                          id='which_day',
                          options=[dict([(i, key) for i in ['label','value']]) for key in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday','Weekends']],
                          value='Monday'
                        ),
                dcc.Graph(id='stat_chart'),
                ]),
        
        
        # dcc.Store inside the app that stores the intermediate value
        dcc.Store(id='intermediate-value')
        ])

@app.callback(
        Output(component_id='show_custom',component_property='style'),
        [Input('Show_hidden',component_property='value')])
def show_custom_elements(visibility):
    try:
        if 'Show' in visibility:
            return {'display':'block'}
        else:
            return {'display':'none'}
    except TypeError:
        return {'display':'none'}

@app.callback(
        Output('line-chart','figure'),
        [Input('checklist','value'),
         Input('intermediate-value','data')])
def update_line_chart(river_level,jsonified_data):
    '''
    update the figure when the user changes which river levels to look at
    '''
    river_stats=pd.read_json(jsonified_data, orient='split')

    print('updating figure',river_level)
    fig = go.Figure()
    # Full line
    fig.add_scattergl(x=river_stats.datetime,
                      y=river_stats.waterlevel, 
                      line={'color': 'black'},
                      name='Water level')

    # Above threshhgold
    for cat in river_level:
        fig.add_scattergl(x=river_stats.datetime,
                          y=river_stats.waterlevel.where(river_stats.level_cat==cat), 
                          line={'color': lcat_colors_dict[cat]},
                          name=cat)
    fig.update_layout(
                xaxis_title='Date',
                yaxis_title='waterlevel/mm')
    return fig


@app.callback(
        Output('intermediate-value', 'data'),
        Output('input_url','value'),
        Output('at_least','value'),
        Output('low','value'),
        Output('medium','value'),
        Output('high','value'),
        Output('my-date-picker-range','start_date'),
        Output('my-date-picker-range','end_date'),
        [Input('which_river','value'),
         Input('number_days','value')])
def update_placeholder(river,days):
    '''
    load new data!
    '''
    print(river,days)
    #try to load the url two times
    try:
        river_st=get_river_stats_url_days(river_stats_dict[river]["url"],days)
    except urllib2.URLError:
        try:
            river_st=get_river_stats_url_days(river_stats_dict[river]["url"],days)
        except urllib2.URLError:
            print("wrong url...")
    river_st=make_categ_waterlevels(river_st,
                                    river_stats_dict[river]["levels"]["at_least"],
                                    river_stats_dict[river]["levels"]["low"],
                                    river_stats_dict[river]["levels"]["medium"],
                                    river_stats_dict[river]["levels"]["high"])
    print('okay,now returning it',
          river_stats_dict[river]["levels"]["at_least"],
          river_stats_dict[river]["levels"]["low"],
          river_stats_dict[river]["levels"]["medium"],
          river_stats_dict[river]["levels"]["high"])
    return river_st.to_json(date_format='iso', orient='split'),river_stats_dict[river]["url"]+str(days),river_stats_dict[river]["levels"]["at_least"],river_stats_dict[river]["levels"]["low"], river_stats_dict[river]["levels"]["medium"],river_stats_dict[river]["levels"]["high"], river_st.datetime.min(),river_st.datetime.max()

@app.callback(
        Output('stat_chart','figure'),
        [Input('which_day','value'),
         Input('intermediate-value','data'),
         Input('my-date-picker-range','start_date'),
         Input('my-date-picker-range','end_date')])
def update_statistics_figure(which_day,jsonified_data,start_date,end_date):  
    river_stats=pd.read_json(jsonified_data, orient='split')  
    river_stats=river_stats[(river_stats.datetime<end_date)&(river_stats.datetime>start_date)]
    if which_day !='Weekends':
        averaged=river_stats[river_stats.weekdays==which_day].groupby(by='day_hour').mean()
        std=river_stats[river_stats.weekdays==which_day].groupby(by='day_hour').std()
        fig = go.Figure()
        fig.add_scattergl(x=averaged.index,
                      y=averaged.waterlevel, 
                      line={'color': 'black'},
                      name='Water level',
                      error_y=dict(
                              type='data',
                              array=std.waterlevel,
                              visible=True))
        fig.update_layout(
                xaxis_title='hours of the day/hours',
                yaxis_title='waterlevel/mm')
        return fig
    else:
        river_stats["weekend"]= river_stats.weekdays== ('Saturday' or 'Sunday')
        averaged=river_stats[river_stats.weekend==True].groupby(by='day_hour').mean()
        std=river_stats[river_stats.weekend==True].groupby(by='day_hour').std()
        fig=go.Figure()
        fig.add_scattergl(x=averaged.index,
                      y=averaged.waterlevel, 
                      line={'color': 'black'},
                      name='Water level',
                      error_y=dict(
                              type='data',
                              array=std.waterlevel,
                              visible=True))
        fig.update_layout(
                xaxis_title='hours of the day/hours',
                yaxis_title='waterlevel/mm')
        return fig
        
app.run_server(debug=True)













