# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 13:18:52 2020

@author: matthew.fligiel
"""

"""
Note - this uses 'vals' from walkscore script, with coordinates of the housing

el, with coordinates of the cta
tvals, with coordinates of buses

both are from the KML parse script
"""
import pandas as pd
import numpy as np
#let's ust take columns we need
pts = vls[['index', 'Address', 'Latitude', 'Longitude']]
elpts = el[['longname', 'latitude', 'longitude']]
bus = tvals[['public_name', 'latitude', 'longitude']]
bus.columns = ['longname', 'latitude', 'longitude']
pts = pts.dropna().reset_index(drop=True)


from scipy.spatial.distance import cdist
#we'll use it to get distance

###############################
#distance to nearest L stop
###############################
#cdist from points to l
dists = cdist(pts.iloc[:,2:], elpts.iloc[:,1:3], metric='cityblock')
#argmin of each to get the closest
idx = np.argmin(dists, axis=1)
#pull the distances and stops into a df
closest_L_distance = pd.DataFrame({'dist':np.min(dists, axis=1)*69.2})
closest_L_stop = elpts.loc[idx, ['longname']].reset_index(drop=True)
closest_L = pd.concat([pts, closest_L_distance, closest_L_stop], axis=1, ignore_index=True)
closest_L.columns = ['index', 'Address', 'Lat', 'Long', 'L_Distance', 'L_Stop']

#############################
#distance to nearest bus stop
#############################
#get distances of each
dists_bus = cdist(pts.iloc[:,2:], bus.iloc[:,1:3], metric='cityblock')
#argmin of each
idx_bus = np.argmin(dists_bus, axis=1)
#pull the distances and stops into a df
closest_bus_distance = pd.DataFrame({'dist':np.min(dists_bus, axis=1)*69.2})
closest_bus_stop = bus.loc[idx_bus, ['longname']].reset_index(drop=True)
closest_bus = pd.concat([pts, closest_bus_distance, closest_bus_stop], axis=1, ignore_index=True)
closest_bus.columns = ['index', 'Address', 'Lat', 'Long', 'Bus_Distance', 'Bus_Stop']


###############################
#number of routes within 1 mile
#not pulling in distances as just getting routes
###############################
#get those within a mile
idx_close_bus = pd.DataFrame(np.argwhere(dists_bus*69.2 < 1))

#merge the close buses and housing,
#then merge in buses,
#aggregate routes and nightroutes as sets on address
from functools import reduce
address_bus_routes =\
pd.merge(pts, idx_close_bus, left_index=True, right_on=0, how='inner')\
    .merge(tvals, left_on = 1, right_index=True, how='inner').groupby('index')\
        .agg({'routes': lambda x: reduce(set.union, x), \
             'owlroutes': lambda x: reduce(set.union, x)})

        

################################ 
#number of l stops within 1 mile
################################
#same logic as above
idx_close_L = pd.DataFrame(np.argwhere(dists*69.2 < 1))
#the below line only needs to be run once
#el.lines = el.lines.apply(lambda x: set(x.replace(" ", "").split(',')))
address_L_lines =\
pd.merge(pts, idx_close_L, left_index=True, right_on=0, how='inner')\
    .merge(el, left_on = 1, right_index=True, how='inner').\
        groupby('index').agg({'lines': lambda x: \
              reduce(set.union, x)})
#if it's null, that means there's no L within a mile...eek.
#slightly fewer rows since it's by address
            
##########
#Export
##########
closest_bus.merge(closest_L).to_csv("Closest_L_Bus.csv")         
#my tables above are pretty but it may be better to just export it normalized
close_L_lines = pd.merge(pts, idx_close_L, left_index=True, right_on=0, how='inner')\
    .merge(el, left_on = 1, right_index=True, how='inner').iloc[:,[0,1,2,3,6,8,9]]\
        .sort_values('index')
close_L_lines['lines'] = close_L_lines.lines.apply(list)

close_L_lines.explode('lines').to_csv("Close_L_Lines.csv", index=False)          

#bus
pd.merge(pts, idx_close_bus, left_index=True, right_on=0, how='inner')\
    .merge(tvals, left_on = 1, right_index=True, how='inner').\
        iloc[:,[0,1,2,3,6,9,10]].sort_values('index').\
            to_csv("Close_Bus_Routes.csv", index=False)