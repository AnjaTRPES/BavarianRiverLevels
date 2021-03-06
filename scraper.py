#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 31 15:58:57 2021

@author: anja
"""

import numpy as np
import pandas as pd
import urllib.error
import matplotlib.pyplot as plt


def get_river_stats_url(url):
    dfs=pd.read_html(url)
    river_stats=dfs[0]
    river_stats[river_stats.columns[0]]=pd.to_datetime(river_stats[river_stats.columns[0]],
           format='%d.%m.%Y %H:%M')
    river_stats['hours']=(river_stats[river_stats.columns[0]]-river_stats[river_stats.columns[0]][0])/np.timedelta64(1,'h')
    river_stats=river_stats.rename(columns={river_stats.columns[0]:'datetime',
                                          river_stats.columns[1]:'waterlevel'})
    return river_stats

def get_river_stats_url_days(url,days):
    dfs=pd.read_html(url+str(days))
    river_stats=dfs[0]
    river_stats[river_stats.columns[0]]=pd.to_datetime(river_stats[river_stats.columns[0]],
           format='%d.%m.%Y %H:%M')
    river_stats['hours']=(river_stats[river_stats.columns[0]]-river_stats[river_stats.columns[0]][0])/np.timedelta64(1,'h')
    river_stats=river_stats.rename(columns={river_stats.columns[0]:'datetime',
                                          river_stats.columns[1]:'waterlevel'})
    return river_stats
    

def get_river_stats(Region,Station, days):
    """
    Download the rivers water levels at a particular station over x days
    region: str, Region where the river is found, ex. isar for the loisach river
    station: measuring station with an unique identifier unfortunately e.g.
        garmisch-o-d-partnachmuendung-16401006
    days: int, number of days to be looked at
    
    returns:
        Dataframe with datetime, level, hours
    """
    html='https://www.hnd.bayern.de/pegel/'+Region+'/'
    html+=Station+'/tabelle?methode=wasserstand&days='+str(days)
    return get_river_stats_url(html)

def make_categ_waterlevels(river_stats,at_least=90,low=100,medium=120,high=170):
    river_stats['level_cat']=pd.cut(river_stats.waterlevel,
               bins=[0,at_least,low,medium,high,high*10000],include_lowest=True,
               right=True,
               labels=['too low','low','medium','high','too high'])
    #add the days of the week
    river_stats['weekdays']=river_stats.datetime.dt.day_name()
    river_stats['day_hour']=river_stats.datetime.dt.hour
    return river_stats

if __name__=='__main__':
    river_stats=get_river_stats('isar','garmisch-o-d-partnachmuendung-16401006',360)
    plt.figure()
    plt.plot(river_stats['hours'],river_stats[river_stats.columns[1]],'o-')
    #plt.plot(river_stats['hours'])
    plt.show()



