#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May 16 15:55:43 2018

@author: MinBin
"""

# import packages
import os
import requests
import itertools
import logging
import copy

from bs4 import BeautifulSoup
import pandas as pd
import dill
import folium
from folium.plugins import MarkerCluster
from scipy.spatial.distance import squareform

# google map api (2,500 free requests per day): geocoding and distance matrix
# api key: https://developers.google.com/maps/documentation/geocoding/get-api-key
import googlemaps
gmaps = googlemaps.Client(key = 'ENTER YOUR KEY HERE')

logger = logging.getLogger("DataCollection")
logger.basicConfig = logging.basicConfig(level=logging.DEBUG)
# Pickle file names
DISTANCE_PKL = 'distance.pkl'
GEOCODED_DATA_PKL = 'geocoded_data.pkl'
SORTED_DISTANCE_PKL = 'sorted_distance.pkl'
DISTANCE_MATRIX_PKL = 'distance_matrix.pkl'

def sort_distance(distances):
    """
    Takes in distance list and sorts so that
    the largest sublists (elements that share the same name)
    are first. Also, it sorts the distance values from 0->n for each
    sublist
    """
    # get first value in pair e.g.  `shop 135425` in 
    # (2623, 'shop 135425 / shop 135942')
    distances_by_type_id = {}
    
    for entry in distances:

        type_id, _ = Data.split_pair(entry[1])
        if distances_by_type_id.get(type_id, None) is None:
            distances_by_type_id[type_id] = []
            
        distances_by_type_id[type_id] += [entry]
        
    # get items, we want to sort the list of lists
    distances_list = distances_by_type_id.items()
    # grab the sublists from the tuple
    distances_list = [l for name, l in distances_list]
    # sort the list from biggest to smallest
    distances_list = sorted(distances_list, key=len, reverse=True)
    
    # sort the sublists
    distances_list = [sorted(l) for l in distances_list]
        
    flat_list = [elem for sublist in distances_list for elem in sublist]
            
    return flat_list
    
             
class DataEntry(object):
    """
    Class for each place in the dataset. Stores information about each location
    including latitude and longitude.
    """
    def __init__(self, name, address, entry_id, entry_type):
        self.name = name.encode('utf-8') if type(name) is unicode else name
        self.address = address.encode('utf-8') if type(address) is unicode else address
        self.entry_id = entry_id
        self.entry_type = entry_type
        self.lat = None
        self.lon = None
        
    def __repr__(self):
        return '%s %s (%s) at address %s (%s, %s)' % (
                self.entry_type, self.entry_id,
                self.name, self.address,
                self.lat, self.lon)
    
    @classmethod
    def from_dict(cls, de_dict):
        return cls(name=de_dict['name'], address=de_dict['address'], 
                   entry_id=de_dict['entry_id'], entry_type=de_dict['entry_type'])
            
    def to_dict(self):
        return {'name': self.name, 'address': self.address, 
                'entry_id': self.entry_id, 'entry_type': self.entry_type}
    
class Data(object):
    """
    Class for storing DataEntry objects (places).
    """
    TYPES = {
            'shop': 'shop',
            'warehouse': 'warehouse',
            }
   
    def __init__(self):
        self.warehouse_id = None
        self.shop_id = None
        
        self.shops = []
        self.warehouses = []
        
        self.all = []
        
    def __len__(self):
        return len(self.data.all)

    def __repr__(self):
        return '%d shops, %d warehouses' % (
                len(self.shops), len(self.warehouses))
        
    def _next_id(self, id_val):
        # initial case, return 0 when not set
        if id_val is None:
            id_val = 0
            return id_val
        
        # 1...n case
        id_val += 1
        
        return id_val
    
    def next_warehouse_id(self):
        self.warehouse_id = self._next_id(self.warehouse_id)
        return self.warehouse_id
        
    def add_shop(self, shop_data):
        self.shops += [shop_data]
        self.all += [shop_data]
        
    def add_warehouse(self, wh_data):
        self.warehouses += [wh_data]
        self.all += [wh_data]
        
    def find(self, type_id):
        # type_id str in format "data.TYPES <int_id>"
        entry_type, entry_id = type_id.split(' ')
        for elem in self.all:
            if elem.entry_type == entry_type and elem.entry_id == int(entry_id):
                return elem
            
        return None

    def get_pair(self, pair_str):
        id_one, id_two = Data.split_pair(pair_str)
        place_one = self.find(id_one)
        place_two = self.find(id_two)
        
        if place_one is None or place_two is None:
            raise Exception("Couldn't find place given str '%s' or '%s'" % (id_one, id_two))
        else:
            return place_one, place_two
    
    @classmethod
    def split_pair(cls, pair_str):
        # like "shop 119478 / warehouse 01"
        return [e.strip() for e in pair_str.split('/')]
    
    @classmethod
    def make_type_id(cls, place):
        return ' '.join([place.entry_type, str(place.entry_id)])
    
    @classmethod
    def make_pair(cls, place_one, place_two):
        # take two places, return a string identifying the pair
        return ' '.join([cls.make_type_id(place_one), '/', cls.make_type_id(place_two)])

if os.path.exists(GEOCODED_DATA_PKL):
    logger.info("Found pickled file %s, loading...", GEOCODED_DATA_PKL)
    data = dill.load(open(GEOCODED_DATA_PKL))
else:
    data = Data()
    
    ############################################################
    ### add warehouse ###
    
    logger.info("Adding warehouse")
    wh = DataEntry(name='倉庫', address='台北市忠孝東路四段560號', 
                   entry_type=data.TYPES['warehouse'], entry_id=data.next_warehouse_id())
    data.add_warehouse(wh)
    
    ############################################################
    ### 711s data ###      
    
    logger.info("Fetching 711 shop data")
    # target area: Xinyi District, Taipei city(zipcode: 110)
    URL_711 = 'https://www.ibon.com.tw/retail_inquiry_ajax.aspx'
    DISTRICT = '110'
    url_data = {
            'strTargetField': 'ZIPCODE',
            'strKeyWords': '%s' % DISTRICT
            }
    
    response_711 = requests.post(URL_711, data=url_data)
    
    soup_711 = BeautifulSoup(response_711.text, 'lxml')
    table_711 = soup_711.select('table')
    
    tables = soup_711.select('table')
    for table in tables:
        rows = table.find_all('tr')
        # first is header
        rows.pop(0)
        
        for row in rows:
            cols = row.find_all('td')
            cols = [elem.text.strip() for elem in cols]
    
            if cols:
                shop_data = DataEntry(name=cols[1], address=cols[2],
                                    entry_type=data.TYPES['shop'], entry_id=int(cols[0]))
                data.add_shop(shop_data)
                
    logger.info("Fetched %d shops", len(data.shops))
    
    ############################################################
    # convert all the address into geocode (Latitude,Longitude)
    
    logger.info("Beginning geocoding")
    for place in data.all:
        logger.info("Geocoding %s", place.name)
        code = gmaps.geocode(place.address)
        place.lat = code[0]['geometry']['location']['lat']
        place.lon = code[0]['geometry']['location']['lng']
    
    dill.dump(data, open(GEOCODED_DATA_PKL, "w"))
    
############################################################
# create interaction map

xinyi_coordinates = (25.033964, 121.564468)
xinyi_map = folium.Map(location=xinyi_coordinates,
                       tiles='Stamen Toner',
                       zoom_start=10)

# create cluster
mc = MarkerCluster()
for place in data.all:   
    # colour warehouse specially
    if place.entry_type == data.TYPES['warehouse']:
        logger.info("found warehouse")
        folium.Marker(location=[place.lat, place.lon],
                      icon=folium.Icon(icon='circle',color='red')
                      ).add_to(xinyi_map)
    else:
        mc.add_child(folium.Marker(location=[place.lat, place.lon], 
                                   popup=place.name.decode('utf-8'),
                                   icon=folium.Icon(icon='circle',color='blue')))
                    
xinyi_map.add_child(mc)
xinyi_map.save("map_xinyi.html")

############################################################
# create distance list (sorted with 0) and distance matrix (pairwise distance): in meter

if os.path.exists(DISTANCE_PKL):
    logger.info("Found pickled file %s, loading...", DISTANCE_PKL)
    distance = dill.load(open(DISTANCE_PKL))
else:
    
    distance = []
    
    # get all combinations of every place with every other place
    for place_one, place_two in itertools.combinations(data.all, 2):
        logger.info("Calculating distance for %s and %s", place_one, place_two)
        response = gmaps.distance_matrix((place_one.lat, place_one.lon), (place_two.lat, place_two.lon))
        # 'OK' in, .... because the response strings are unicode
        if 'OK' in response['status']:
            # only have one row because we have one origin and one destination
            row = response['rows'][0]
            elem = row['elements'][0]
            if 'OK' in elem['status']:
                distance.append((elem['distance']['value'], Data.make_pair(place_one, place_two)))
            
    dill.dump(distance, open(DISTANCE_PKL, "w"))

### distance list ###
unsorted_distance = copy.deepcopy(distance)
logger.info("Adding 0 distances -- each place with itself")
# add self distance (0) into distance list
for elem in data.all:
    elem = (0, Data.make_pair(elem, elem))
    unsorted_distance.append(elem)
# we want to group all 0 distances as the first in the list, and all elements with same name together
sorted_distance = sort_distance(unsorted_distance)

# delete non-required data and save sorted distance
del unsorted_distance
dill.dump(sorted_distance, open(SORTED_DISTANCE_PKL, "w"))

### distance matrix ###
# extract distance value
distance_values = [value[0] for value in distance]
# form an squareform arrary
distance_entries = [
        Data.split_pair(d[1])[0] for d in sorted_distance if d[0] == 0]
distance_matrix = pd.DataFrame(
        squareform(distance_values), columns=distance_entries , 
        index=distance_entries)

dill.dump(distance_matrix, open(DISTANCE_MATRIX_PKL, "w"))
distance_matrix.to_csv(open('matrix.csv', 'w'), sep = ',')
