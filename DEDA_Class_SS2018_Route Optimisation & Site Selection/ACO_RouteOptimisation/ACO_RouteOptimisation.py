#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""

@author: MinBin

"""

# import packages        
import dill
from operator import itemgetter
from collections import OrderedDict

import polyline
import folium


import googlemaps

from ACO_DataCollection import Data
from ACO_Algorithm import MMAS

# google map api (2,500 free requests per day): geocoding and distance matrix
# api key: https://developers.google.com/maps/documentation/geocoding/get-api-key
gmaps = googlemaps.Client(key ='ENTER YOUR KEY HERE')

# Pickle file names
GEOCODED_DATA_PKL = 'geocoded_data.pkl'
DISTANCE_MATRIX_PKL = 'distance_matrix.pkl'
PLACE_INFO_PKL = 'place_info.pkl'
PLACE_NAMES_PKL = 'place_names.pkl'
PLACE_DICT_PKL = 'place_dict.pkl'

############################################################
# load required data

data = dill.load(open(GEOCODED_DATA_PKL)) 
distance_matrix = dill.load(open(DISTANCE_MATRIX_PKL)) 
place_names = dill.load(open(PLACE_NAMES_PKL))
place_dict = dill.load(open(PLACE_DICT_PKL))

############################################################
# data processing
   
dist_zipped = zip(place_names, zip(*distance_matrix))
dist_dict = {}
for key, vals in dist_zipped:
    dist_dict[key] = {}
    for i, item in enumerate(vals):
        dist_dict[key][place_names[i]] = item
    
sorted_dist_dict = {}
# sort the distance dictionary by values
for key in dist_dict.keys():
    sorted_tuples = sorted(dist_dict[key].items(), key=itemgetter(1))
    ordered_subdict = OrderedDict(sorted_tuples)
    sorted_dist_dict[key] = ordered_subdict
        
dist_dict = sorted_dist_dict
 
############################################################       
# apply ACO ###

aco = MMAS(init_place='warehouse 0',num_iters=2000, num_ants=50,
           alpha=1, beta=3, rho=0.3,
            q=80, place_dict=place_dict,dist_dict=dist_dict)

aco.addPlace()
aco.Search()  

############################################################
### polyline ###

# generate polyline for each path from google direction api
directions_results = {}
for i in range(len(aco.BestTour)):
    currPlace = aco.BestTour[i]
    # only compute till the last place
    if i != (len(aco.BestTour)-1):
        nextPlace = aco.BestTour[i+1]
        directions_results[i] = gmaps.directions(place_dict[currPlace],
                          place_dict[nextPlace])

############################################################        
### map the route ###
        
xinyi_coordinates = (25.033964, 121.564468)
route_map = folium.Map(location=xinyi_coordinates,
                       zoom_start=15)

# layer control 
folium.TileLayer('openstreetmap').add_to(route_map)
folium.TileLayer('stamenwatercolor').add_to(route_map)
folium.TileLayer('Stamen Toner').add_to(route_map)
folium.LayerControl().add_to(route_map)

# icon in the map
logo_WH = './pic/warehouse.png'
logo_end = './pic/end_shop.png'
logo_shop = './pic/shop.png'

for place in data.all:   
    # colour warehouse specially
    info = (place.name+str(place.entry_id)).decode('utf-8')
    if place.entry_type == data.TYPES['warehouse']:
        icon_WH = folium.features.CustomIcon(logo_WH,icon_size=(50, 50)) 
        folium.Marker(location=[place.lat, place.lon],
                      popup=info,
                      icon=icon_WH
                      ).add_to(route_map)
    # point out the last shop
    elif Data.make_type_id(place) == aco.BestTour[-2]:
        icon_end = folium.features.CustomIcon(logo_end,icon_size=(50, 50))
        folium.Marker(location=[place.lat, place.lon], 
                      popup=info,
                      icon=icon_end
                      ).add_to(route_map)
    else:
        icon_shop = folium.features.CustomIcon(logo_shop,icon_size=(40, 40))
        folium.Marker(location=[place.lat, place.lon], 
                      popup=info,
                      icon=icon_shop
                      ).add_to(route_map)
        
color_list = ['#253494','#2c7fb8','#41b6c4','#a1dab4','#ffffcc']
                   
for p in range(len(directions_results)):
    # decode all the polyline (overview_polyline)
    path = polyline.decode(directions_results[p][0]['overview_polyline']['points'])
    # map the path
    color = color_list[p%5]
    folium.PolyLine(path, 
                    color=color, 
                    weight=5, 
                    opacity=1).add_to(route_map)

route_map.save("route_map.html")

