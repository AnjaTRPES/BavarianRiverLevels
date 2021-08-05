#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 07:35:17 2021

@author: anja
"""

#A dictionairy containing the river names, urls, and waterlevels
import pickle




river_stats_dict={"Loisach":{"url":"https://www.hnd.bayern.de/pegel/isar/garmisch-o-d-partnachmuendung-16401006/tabelle?methode=wasserstand&days=",
                             "levels":
                                 {'at_least':90,"low":100,"medium":120,"high":170}
                                 },
                "Ammer_Peisenberg":{"url":"https://www.hnd.bayern.de/pegel/isar/peissenberg-16612001/tabelle?methode=wasserstand&days=",
                                    "levels":
                                        {'at_least':10,"low":20,"medium":40,"high":110}
                                        }
                    }

        

with open('river_stats.json', 'wb') as fp:
    pickle.dump(river_stats_dict, fp)