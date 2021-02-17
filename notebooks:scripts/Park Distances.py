# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 10:40:39 2020

@author: matthew.fligiel
"""
import pandas as pd
import json
from shapely.geometry import shape, GeometryCollection

#open file
refilename = "Parks - Chicago Park District Park Boundaries (current).geojson"
with open(pth+refilename) as f:
  features = json.load(f)["features"]

# NOTE: buffer(0) is a trick for fixing scenarios where polygons have overlapping coordinates 
mapp = GeometryCollection([shape(feature["geometry"]).buffer(0) for feature in features])

#Pulling labels
lbl = [feature["properties"]["label"] for feature in features]
#pulling shapes
geoms = [feature["geometry"] for feature in features]
shapes = [shape(geom) for geom in geoms]

#making df
shapedf = pd.DataFrame()
shapedf['name'] = lbl
shapedf['shape'] = shapes


#park distance table
#cross join
def cartesian_product_basic(left, right):
    return (
       left.assign(key=1).merge(right.assign(key=1), on='key').drop('key', 1))

#make a df
parkdistances = cartesian_product_basic(pts, shapedf)

#get lat long for each row
def relonglat(row):
     return Point(row['Longitude'], row['Latitude'])

#this part is fairly slow and inefficient...i should realistically 
#get the point before the cartesian join...
parkdistances['Point'] = parkdistances.apply(relonglat, axis=1)

#also slow.  69.2 to get actual distance
parkdistances['pdists']=\
parkdistances.apply(lambda x: x['Point'].distance(x['shape'])*69.2, axis=1)

#Let's get the closest!
closest_park = parkdistances.loc\
    [parkdistances.groupby(['index','Address']).\
     agg({'pdists':'idxmin'}).pdists.values,:]
#round the numbers
closest_park['pdists'] = closest_park.pdists.apply(lambda x: "%.5f" % round(x,5))
closest_park.to_excel("Closest_park.xlsx")
closest_park.loc[:,['index', 'Address', 'Latitude', 'Longitude', 'name', 'pdists']]\
.to_csv("Closest_park.csv", index=False)
#some of these (such as the one for 15) are unimproved parks.
#pull in properties if we want...later
pd.DataFrame([i['properties'] for i in features])