# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 13:29:55 2020

@author: matthew.fligiel
"""
import pandas as pd
#set the path, and import the file
pth = "C:/Users/matthew.fligiel/OneDrive - Accenture/Documents/MSCA/MSCA 31012/\
Final Project/"
vals = pd.read_csv(pth+"Affordable_Rental_Housing_Developments.csv") 


#cleaning the address column, purely for the web address
qry = vals['Address'].str.replace('.', '', regex=False). \
str.replace(' ', '-')
#cleaning the address - some are a block of addresses, we only use the first
vals['Address'] = vals['Address'].str.replace('-..?', '', regex=True)
#fix the mis-spellings
vals['Address'] = vals.Address.str.replace('Larabee', 'Larrabee')
vals['Address'] = vals.Address.str.replace('Indepenednece', 'Independence')
#make the address to use in parsing
vals['vtouse'] = qry.astype(str)+'-chicago-il-'+vals['Zip Code'].astype(str)


#geocode anything with no address
#first, we create a locator, then pull lat long, then update our df.
from geopy.geocoders import Nominatim

locator = Nominatim(user_agent="myGeocoder")
for index, row in vals.iterrows():
    if(pd.isnull(row['Latitude'])):
        vl =row['Address'] + ', Chicago, IL'
        location = locator.geocode(vl)
        print(row['Address'] + ', Chicago, IL')
        vals.loc[index, 'Latitude'] = location.latitude
        vals.loc[index, 'Longitude'] = location.longitude

#legacy from earlier code - make sure we have no dashes!
vls = vals[vals['Address' ].str.contains('-')==False].copy() #empty, but holdover
vls.reset_index(inplace=True)

from bs4 import BeautifulSoup, Comment
import requests
import re

#this loop pulls the walk, transit, bike scores.
for i in range(len(vls)):
    #pull down the html for the address
    sd = requests.get("https://www.walkscore.com/score/"+vls.loc[i, 'vtouse'])
    #parse the HTML
    soop = BeautifulSoup(sd.text, 'html.parser')
    #look for the class below, which indicates the scores
    thrscrs1 = soop.find_all(class_ = "block-header-badge score-info-link")
    #iterate over the class dividers, and pull out the comments, where the scores are
    tc1 = [v.find(text=lambda text:isinstance(text, Comment)) for v in thrscrs1]
    #find the pieces with the score type and score
    strs1 = [re.search('badge(.*)png', v).group(0) for v in tc1]
    #join them into a string, which can be used
    fv = ''.join(str(elem) for elem in strs1)
    #put them into a column
    vls.at[i, 'ffff'] = fv
    print(i, fv)
  
"""
#died at 206 due to too many connections, so stopped and restarted
for i in range(205, len(vls)):
    #print(vals.loc[i,'vtouse'])
    sd = requests.get("https://www.walkscore.com/score/"+vls.loc[i, 'vtouse'])
    soop = BeautifulSoup(sd.text, 'html.parser')
    thrscrs1 = soop.find_all(class_ = "block-header-badge score-info-link")
    tc1 = [v.find(text=lambda text:isinstance(text, Comment)) for v in thrscrs1]
    strs1 = [re.search('badge(.*)png', v).group(0) for v in tc1]
    fv = ''.join(str(elem) for elem in strs1)
    vls.at[i, 'ffff'] = fv
    print(i, fv)
"""
#save a copy at this point just in case
vlscopy = vls.copy()
#add the walkscore
vls['Walkscore'] = vls.ffff.str.extract('badge/walk/score/(?P<Walkscore>.*?).png').astype(int)
#add the bikescore
vls['Bikescore'] = vls.ffff.str.extract('badge/bike/score/(?P<Bikescore>.*?).png').astype(int)
#add the transitscore
vls['Transitscore'] = vls.ffff.str.extract('badge/transit/score/(?P<Transitscore>.*?).png').astype(int)
del vls['ffff']

vls.to_excel("Developments, with scores.xlsx")
vls.to_csv("Developments, with scores.csv", index=False)