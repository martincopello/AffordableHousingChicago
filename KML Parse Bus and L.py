# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 13:23:29 2020

@author: matthew.fligiel
"""



from pykml import parser
import pandas as pd
from bs4 import BeautifulSoup

#Pull in and open the file
pth = "C:/Users/matthew.fligiel/OneDrive - Accenture/Documents/MSCA/MSCA 31012/\
Final Project/"
filename='CTA_BusStops.kml'
fl = pth+filename
with open(fl) as f:
    folder = parser.parse(f).getroot().Document.Folder

#can use beautiful soup to pull in more!
#create lists to pull into from KML file
plnm=[]
cordi=[]
routes = []
owlroutes = []
strt = []
cstrt = []
pname = []
status = []
#loop over each parent node(placemark type)
for pm in folder.Placemark:
    plnm1=pm.name
    plcs1=pm.Point.coordinates
    plnm.append(plnm1.text)
    cordi.append(plcs1.text)
    #we use beautiful soup to parse the html structure, and pull in info
    spp = BeautifulSoup(str(pm.description), 'html.parser')
    rts = spp.find("td", text="ROUTESSTPG").find_next_sibling("td").text
    owl = spp.find("td", text="OWLROUTES").find_next_sibling("td").text
    routes.append(rts)
    owlroutes.append(owl)
    strt.append(spp.find("td", text="STREET").find_next_sibling("td").text)
    cstrt.append(spp.find("td", text="CROSS_ST").find_next_sibling("td").text)
    pname.append(spp.find("td", text="PUBLIC_NAME").find_next_sibling("td").text)
    status.append(spp.find("td", text="STATUS").find_next_sibling("td").text)
    
#create the dataframe
db=pd.DataFrame()
db['place_name']=plnm
db['cordinates']=cordi
db['routes'] = routes
db['owlroutes'] = owlroutes
db['street'] = strt
db['cross_st'] = cstrt
db['public_name'] = pname
db['status'] = status

#now, using the street, cross st, public name, status, I can look more closely.
db[['place_name', 'status']].groupby('status').count() 
#not many no in service,we can remove them if needed.  flag seem to have no route.
#ignore temp stops too, and unposted

stops = db[db['status'] == 'In Service'].copy()

#group by public name
cds =  stops.cordinates.str.split(',',expand=True)
cds.columns = ['longitude', 'latitude', 'ff']
stops = pd.merge(stops, cds, left_index=True, right_index=True)
del stops['ff']

#extract lat and long
pd.options.display.float_format = '${:,.20g}'.format
stops['latitude'] = stops['latitude'].astype(float)
stops['longitude'] = stops['longitude'].astype(float)


#test this merge
tvals = stops[['public_name', 'latitude', 'longitude', 'routes', 'owlroutes']].copy()
#clean up routes
tvals['routes'] = tvals.routes.str.split(',')
tvals['owlroutes'] = tvals.owlroutes.str.split(' ')
#get mean lat long for each stop, as the stop going each way is separate
tvals = stops.groupby('public_name').\
    agg({'latitude':'mean','longitude':'mean', \
         'routes':lambda x: ','.join(x), 'owlroutes':lambda x: ','.join(x)})
#split them, make them sets, and count the numbers
tvals['routes'] = tvals.routes.str.split(',')
tvals['routes'] = tvals.routes.apply(set)
tvals['numroutes'] = tvals.routes.apply(len)
#remove cases that aren't real and dont start with N
tvals['owlroutes']= tvals['owlroutes'].str.replace('<Null>', '', regex=True)\
    .replace('^[^N].*','',regex=True)
tvals['owlroutes'] = tvals.owlroutes.str.split(',')
#create sets and length
tvals['owlroutes'] = tvals.owlroutes.apply(set)
tvals['numowlroutes'] = tvals.owlroutes.apply(len)
#clean index
tvals.reset_index(level=0, inplace=True)

#CTA STOPS
#similar to above, parse in the file
pth = "C:/Users/matthew.fligiel/OneDrive - Accenture/Documents/MSCA/MSCA 31012/\
Final Project/"
filename='CTA_RailStations.kml'
fl = pth+filename
with open(fl) as f:
    folder = parser.parse(f).getroot().Document.Folder
    
plnm=[]
cordi=[]
ln = []
lines = []
for pm in folder.Placemark:
    plnm1=pm.name
    plcs1=pm.Point.coordinates
    plnm.append(plnm1.text)
    cordi.append(plcs1.text)
    spp = BeautifulSoup(str(pm.description), 'html.parser')
    ln.append(spp.find("td", text="LONGNAME").find_next_sibling("td").text)
    lines.append(spp.find("td", text="LINES").find_next_sibling("td").text)
 
#create DF
el=pd.DataFrame()
el['place_name']=plnm
el['cordinates']=cordi
el['longname'] = ln
el['lines'] = lines

#Clean up the names with regex
el['lines'] = el['lines'].str.replace('Evanston Express', '').\
    replace('\(([^\)]+)\)', '', regex=True)
el['lines'] = el.lines.str.replace(' Lines?', '', regex=True).\
    replace(' \&', ',', regex=True)
    
#separate out the coordinates
cds =  el.cordinates.str.split(',',expand=True)
cds.columns = ['longitude', 'latitude', 'ff']
el = pd.merge(el, cds, left_index=True, right_index=True)
del el['ff']
    
#to excel
el.to_excel("parsed_el.xlsx")
tvals.to_excel("parsed_bus.xlsx")
    