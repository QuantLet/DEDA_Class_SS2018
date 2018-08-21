#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""

@author: MinBin

"""
# import packages
import os
import requests
import json
import geojson
import ast
import logging
import dill

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import folium
from folium import plugins
from folium import FeatureGroup
import pdfplumber

from shapely.geometry import shape

# google map api (2,500 free requests per day): geocoding and distance matrix
# api key: https://developers.google.com/maps/documentation/geocoding/get-api-key
import googlemaps
gmaps = googlemaps.Client(key = 'ENTER YOUR KEY HERE')

logger = logging.getLogger("DataCollection")
logger.basicConfig = logging.basicConfig(level=logging.DEBUG)

# Pickle file names
GEOCODED_DATA_PKL = 'geocoded_data.pkl'

############################################################

class DataEntry(object):
    """
    Class for each place in the dataset. Stores information about each location
    including latitude and longitude.
    """
    def __init__(self, name, address, entry_id, entry_type, lat, lon):
        self.name = name.encode('utf-8') if type(name) is unicode else name
        self.address = address.encode('utf-8') if type(address) is unicode else address
        self.entry_id = entry_id.encode('utf-8') if type(entry_id) is unicode else entry_id
        self.entry_type = entry_type
        self.lat = lat
        self.lon = lon

    def __repr__(self):
        return '%s %s (%s) at address %s (%s, %s)' % (
                self.entry_type, self.entry_id,
                self.name, self.address,
                self.lat, self.lon)

    @classmethod
    def from_dict(cls, de_dict):
        return cls(name=de_dict['name'], address=de_dict['address'],
                   entry_id=de_dict['entry_id'], entry_type=de_dict['entry_type'],
                   lat=de_dict['lat'], lon=de_dict['lon'])

    def to_dict(self):
        return {'name': self.name, 'address': self.address,
                'entry_id': self.entry_id, 'entry_type': self.entry_type,
                'lat': self.lat, 'lon': self.lon}

class Data(object):
    """
    Class for storing DataEntry objects (places).
    """
    TYPES = {
            'FamilyMart': 'FamilyMart',
            '7-Eleven': '7-Eleven',
            'HiLife': 'HiLife',
            'OKmart': 'OKmart'
            }

    def __init__(self):
        self.FamilyMart_id = None
        self.Eleven_id = None
        self.HiLife_id = None
        self.OKmart_id = None

        self.FamilyMart = []
        self.Eleven = []
        self.HiLife = []
        self.OKmart = []

        self.all = []

    def __len__(self):
        return len(self.data.all)

    def __repr__(self):
        return '%d FamilyMart, %d 7-Eleven, %d HiLife, %d OKmart' % (
                len(self.FamilyMart), len(self.Eleven),
                len(self.HiLife), len(self.OKmart))

    def add_FamilyMart(self, shop_data):
        self.FamilyMart += [shop_data]
        self.all += [shop_data]

    def add_Eleven(self, shop_data):
        self.Eleven += [shop_data]
        self.all += [shop_data]

    def add_HiLife(self, shop_data):
        self.HiLife += [shop_data]
        self.all += [shop_data]

    def add_OKmart(self, shop_data):
        self.OKmart += [shop_data]
        self.all += [shop_data]

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

############################################################
# ony run the total codes when there is no "GEOCODED_DATA_PKL"

if __name__ == '__main__':
    if os.path.exists(GEOCODED_DATA_PKL):
        logger.info("Found pickled file %s, loading...", GEOCODED_DATA_PKL)
        data = dill.load(open(GEOCODED_DATA_PKL))
    else:
        data = Data()

        ############################################################
        ### FamilyMart data ###

        URL_FM = 'http://api.map.com.tw/net/familyShop.aspx?' \
        'searchType=ShopList&type=&city=%E5%8F%B0%E5%8C%97%E5%B8%82&' \
        'area=%E4%BF%A1%E7%BE%A9%E5%8D%80&road=&fun=showStoreList&key=' \
        '6F30E8BF706D653965BDE302661D1241F8BE9EBC'

        # add request condition "Referer" to solve blocking
        headers={'Referer':'http://www.family.com.tw/Marketing/inquiry.aspx'}

        response_FM = requests.get(URL_FM,headers=headers)
        soup_FM = BeautifulSoup(response_FM.text, 'lxml')
        string_data = soup_FM.p.next
        # the data we want is inside of a method, as a string
        # like somethingFunc([data])
        string_data = unicode(string_data)
        start_paren = string_data.find('(') + 1
        end_paren = string_data.find(')')
        inside_parens = string_data[start_paren:end_paren]

        # looks like a dict, quacks like a dict
        data_FM = json.loads(inside_parens)
        # delete redundant string
        for n in range(len(data_FM)):
             data_FM[n]['NAME'] = data_FM[n]['NAME'].replace(u'\u5168\u5bb6','')

        # input data into class
        for i in range(len(data_FM)):
            shop_data = DataEntry(name=data_FM[i]['NAME'],
                                  address=data_FM[i]['addr'],
                                  entry_type=data.TYPES['FamilyMart'],
                                  entry_id=int(data_FM[i]['SERID']),
                                  lat=data_FM[i]['py'],
                                  lon=data_FM[i]['px']
                                  )
            data.add_FamilyMart(shop_data)

        logger.info("Fetched %d FamilyMart", len(data.FamilyMart))

        ############################################################
        ### 7Eleven data ###

        URL_711 = 'https://www.ibon.com.tw/retail_inquiry_ajax.aspx'
        DISTRICT = '110'
        url_data = {
                'strTargetField': 'ZIPCODE',
                'strKeyWords': '%s' % DISTRICT
                }

        response_711 = requests.post(URL_711, data=url_data)

        soup_711 = BeautifulSoup(response_711.text, 'lxml')

        tables = soup_711.select('table')
        for table in tables:
            rows = table.find_all('tr')
            # first is header
            rows.pop(0)
            for row in rows:
                cols = row.find_all('td')
                cols = [elem.text.strip() for elem in cols]
                if cols:
                    shop_data = DataEntry(name=cols[1],
                                          address=cols[2],
                                          entry_type=data.TYPES['7-Eleven'],
                                          entry_id=int(cols[0]),
                                          lat=None,
                                          lon=None
                                          )
                    data.add_Eleven(shop_data)

        logger.info("Fetched %d 711", len(data.Eleven))

        ############################################################
        ### HiLife data ###

        URL_HL = 'http://www.hilife.com.tw/storeInquiry_street.aspx'

        # Use Firefox as the default browser
        driver = webdriver.Firefox() # need to put geckodriver.exe in the bin
        driver.get(URL_HL)

        option1 = Select(driver.find_element_by_id('CITY'))
        option1.select_by_value('台北市'.decode('utf-8'))

        option2 = Select(driver.find_element_by_id('AREA'))
        option2.select_by_value('信義區'.decode('utf-8'))

        page_source = driver.page_source
        soup_HL = BeautifulSoup(page_source, 'lxml')
        rows = soup_HL.select('tr')

        for cols in rows:
            cols1 = soup_HL.find_all('th')
            cols1 = [elem.text.strip() for elem in cols1]
            HL_ids = cols1[0:][::2]
            HL_names = cols1[1:][::2]

            cols2 = soup_HL.find_all('td')
            cols2 = [elem.text.strip() for elem in cols2]
            # remove the empty string data
            cols2 = filter(None, cols2)
            HL_addresses = cols2[0:][::2]


        for i in range(len(HL_ids)):
            shop_data = DataEntry(name=HL_names[i], address=HL_addresses[i],
                                  entry_type=data.TYPES['HiLife'],
                                  entry_id=HL_ids[i],
                                  lat=None,
                                  lon=None
                                  )
            data.add_HiLife(shop_data)

        logger.info("Fetched %d HiLife", len(data.HiLife))

        ############################################################
        ### OKmart data ###

        URL_OK = 'http://www.okmart.com.tw/convenient_shopSearch_Result.aspx?'\
        'city=台北市&zipcode=信義區&key=&service=&service2=&_=1528400761509'
        response_OK = requests.get(URL_OK)
        soup_OK = BeautifulSoup(response_OK.text, 'lxml')

        soup_OK_divs = soup_OK.find_all('div')

        OK_ids = []
        OK_addresses = []

        for div in soup_OK_divs:
            div_string = unicode(div)
            start_paren = div_string.find('(') + 1
            end_paren = div_string.find(')')
            inside_parens = div_string[start_paren:end_paren]

            # use ast here because the unicode response is a string of strings
            # (string with quotes in the string)
            # ast will evaluate the string into its python data types
            inside_parens = inside_parens.encode('utf-8')
            OK_ids.append(ast.literal_eval(inside_parens)[0])
            OK_addresses.append(ast.literal_eval(inside_parens)[1])

        soup_OK_h2 = soup_OK.find_all('h2')
        OK_names = [elem.text.strip() for elem in soup_OK_h2]

        # [:6]: only till '信義崇安店,' other shops don't exist anymore
        for i in range(len(OK_ids[:7])):
            shop_data = DataEntry(name=OK_names[:7][i], address=OK_addresses[:7][i],
                                  entry_type=data.TYPES['OKmart'],
                                  entry_id=OK_ids[:7][i],
                                  lat=None,
                                  lon=None
                                  )
            data.add_OKmart(shop_data)

        logger.info("Fetched %d Okmart", len(data.OKmart))

        logger.info("Fetched %d in total", len(data.all))

        ############################################################
        ### geocoding ###

        # FamilyMart has lat and lon already

        # 7-Eleven
        for place in data.Eleven:
            logger.info("Geocoding %s", place.name)
            code = gmaps.geocode(place.address)
            place.lat = code[0]['geometry']['location']['lat']
            place.lon = code[0]['geometry']['location']['lng']

        # HiLife
        for place in data.HiLife:
            logger.info("Geocoding %s", place.name)
            code = gmaps.geocode(place.address)
            place.lat = code[0]['geometry']['location']['lat']
            place.lon = code[0]['geometry']['location']['lng']

        # OKmart
        for place in data.OKmart:
            logger.info("Geocoding %s", place.name)
            code = gmaps.geocode(place.address)
            place.lat = code[0]['geometry']['location']['lat']
            place.lon = code[0]['geometry']['location']['lng']

        dill.dump(data, open(GEOCODED_DATA_PKL, "w"))

############################################################
### MRT exits data ###

# load Taipei MRT all exits data
mrt_data = geojson.load(open("MRT.geojson", "r"), encoding="Big5").features

exit_geocode = []
exit_names = []
for mrt_exit in range(len(mrt_data)):
    exit_geocode.append(
            (mrt_data[mrt_exit]['geometry']['coordinates'][1],
            mrt_data[mrt_exit]['geometry']['coordinates'][0])
            )
    exit_names.append(mrt_data[mrt_exit]['properties'][u'出入口名稱'])
# all exits information (name:geocode)
mrt_exits = dict(zip(exit_names, exit_geocode))

# import the geocode of the xinyi area (scale)
xinyi_area = geojson.load(open("xinyi_area.json", "r"))

# point in polygon with geojson by shapely
xinyi_poly = shape(xinyi_area.features[0].geometry)

xinyi_exits_list = []
for mrt in mrt_data:
    mrt_point = shape(mrt.geometry)
    if(xinyi_poly.contains(mrt_point)):
       xinyi_exits_list += [mrt.geometry]
xinyi_exit_geocode = [(e['coordinates'][1], e['coordinates'][0]) for e in xinyi_exits_list]

xinyi_exits = {}
# get the name for each coordinate pair in xinyi mrt exits
for addr, mrt_coords in mrt_exits.iteritems():
    for xinyi_coords in xinyi_exit_geocode:
        if xinyi_coords == mrt_coords:
            xinyi_exits[addr] = mrt_coords

############################################################
### population data ("里"li) ###

# extract data from pdf (https://github.com/jsvine/pdfplumber)
pop_pdf = pdfplumber.open('./population.pdf')
# extract each page
page_0 = pop_pdf.pages[0]
page_1 = pop_pdf.pages[1]
# extract tables
pop_table = page_0.extract_table() + page_1.extract_table()

# convert to dataframe
df = pd.DataFrame(pop_table[1:], columns=pop_table[0])
pop_df = df[[u'\u91cc\u5225\nLi',u'\u5408\u8a08\nSub-total']]

# input missing data (due to the table frame)
pop_df.iloc[29][u'\u5408\u8a08\nSub-total'] = 9204

# remove english ()
def remove_ascii(text):
    return ''.join(i for i in text if ord(i)>128)
pop_df[u'\u91cc\u5225\nLi'] = pop_df[u'\u91cc\u5225\nLi'].apply(remove_ascii)

# drop the sum-up row
pop_df = pop_df.drop(df.index[len(pop_df)-1])
# rename the column names
pop_df.columns = ['Li', 'population']
pop_df.population = pop_df.population.astype(int)

############################################################
### load shape data (of whole taipei) ###

li_taipei = geojson.load(open('Li.geojson', 'r'))

# extrat li data only in xinyi area
features = []
for feature in li_taipei['features']:
    if feature['properties']['SECT_NAME'] == u'信義區':
        features.append(feature)
li_taipei['features'] = features
li_xinyi = li_taipei

############################################################
### mapping ###

# create future group for layer controll
group_FM = FeatureGroup(name='FamilyMart')
group_711 = FeatureGroup(name='7-Eleven')
group_HL = FeatureGroup(name='HiLife')
group_OK = FeatureGroup(name='OKmart')
group_mrt = FeatureGroup(name='MRT')
group_heat =  FeatureGroup(name='Heatmap')

xinyi_coordinates = (25.033964, 121.564468)
xinyi_map = folium.Map(location=xinyi_coordinates,
                       tiles='Stamen Toner',
                       zoom_start=14)
# icon in the map
logo_FM = './pic/FM.jpg'
logo_711 = './pic/711.jpg'
logo_HL = './pic/HL.jpg'
logo_OK = './pic/OK.jpg'
logo_mrt = './pic/MRT.png'

# choropleth
xinyi_map.choropleth(
 geo_data=li_xinyi,
 data=pop_df,
 columns=['Li', 'population'],
 key_on='feature.properties.LIE_NAME',
 fill_color='PuBuGn', fill_opacity=0.5,line_opacity=1,
 legend_name='Population'
)


for place in data.all:
    icon_FM = folium.features.CustomIcon(logo_FM,icon_size=(25, 25))
    if place.entry_type == data.TYPES['FamilyMart']:
        folium.Marker(location=[place.lat, place.lon],
                      icon=icon_FM
                      ).add_to(group_FM)
    xinyi_map.add_child(group_FM)

    icon_711 = folium.features.CustomIcon(logo_711,icon_size=(25, 25))
    if place.entry_type == data.TYPES['7-Eleven']:
        folium.Marker(location=[place.lat, place.lon],
                      icon=icon_711
                      ).add_to(group_711)
    xinyi_map.add_child(group_711)

    icon_HL = folium.features.CustomIcon(logo_HL,icon_size=(25, 25))
    if place.entry_type == data.TYPES['HiLife']:
        folium.Marker(location=[place.lat, place.lon],
                      icon=icon_HL
                      ).add_to(group_HL)
    xinyi_map.add_child(group_HL)

    icon_OK = folium.features.CustomIcon(logo_OK,icon_size=(25, 25))
    if place.entry_type == data.TYPES['OKmart']:
        folium.Marker(location=[place.lat, place.lon],
                      icon=icon_OK
                      ).add_to(group_OK)
    xinyi_map.add_child(group_OK)

for lat, lon in xinyi_exits.itervalues():
    icon_mrt = folium.features.CustomIcon(logo_mrt,icon_size=(25, 25))
    folium.Marker(location=[lat, lon],
                      icon=icon_mrt
                      ).add_to(group_mrt)
    xinyi_map.add_child(group_mrt)

# heatmap
for place in data.all:
    folium.CircleMarker(location=[place.lat, place.lon],
                        radius=1,
                        opacity = 0
                       ).add_to(group_heat)
    xinyi_map.add_child(group_heat)
geocode = pd.DataFrame([(place.lat, place.lon) for place in data.all]).values.tolist()
group_heat.add_child(plugins.HeatMap(geocode, radius=40))

# add layer control
folium.LayerControl().add_to(xinyi_map)

xinyi_map.save("xinyi_map.html")
