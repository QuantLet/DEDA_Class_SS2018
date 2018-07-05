# -*- coding: utf-8 -*-
"""
Created on Tue Jul  3 21:50:36 2018

@author: VWRZTS0
"""

#Load library
import os
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd

#Load information about the World Cup (rounds, teams etc.)
codes = open('C:/Users/VWRZTS0/Desktop/DEDA/DEDA/datasets/countries_codes_and_coordinates.csv','r')
codes= codes.readlines()
codes = [i.replace('"',"") for i in codes]
codes = [i.split(",") for i in codes]
codes = pd.DataFrame(codes)
codes.columns = codes.iloc[0]
codes = codes.drop(0)
codes = codes.drop(columns=['Alpha-2 code','Numeric code'])
codes = codes.iloc[:,:-1]
codes = codes[codes['Alpha-3 code'].map(len) > 3]
codes = codes.drop_duplicates(subset='Country')
codes['Alpha-3 code'] = codes['Alpha-3 code'].str.lstrip()

#Read all World Cup matches
wcmatches = open('C:/Users/VWRZTS0/Desktop/DEDA/DEDA/datasets/WorldCupMatches.csv','r')
wcmatches = wcmatches.readlines()
wcmatches = [i.replace('"',"") for i in wcmatches]
wcmatches = [i.replace("\n","") for i in wcmatches]
wcmatches = [i.replace("rn>","") for i in wcmatches]
wcmatches = [i.split(",") for i in wcmatches]
wcmatches = pd.DataFrame(wcmatches)
wcmatches.columns = wcmatches.iloc[0]
wcmatches = wcmatches.drop(0)
wcmatches = wcmatches.drop(columns=['Datetime','Stage','Stadium','City',
                                    'Win conditions','Attendance',
                                    'Half-time Home Goals','Half-time Away Goals',
                                    'Referee','Assistant 1','Assistant 2',
                                    'RoundID','MatchID','Home Team Initials',
                                    'Away Team Initials'])
wcmatches['Home Team Goals'] = wcmatches['Home Team Goals'].apply(pd.to_numeric)
wcmatches['Away Team Goals'] = wcmatches['Away Team Goals'].apply(pd.to_numeric)
wcmatches = wcmatches.iloc[:852,:]

#Read all World Cup Winners
wcwinners = pd.read_excel('C:/Users/VWRZTS0/Desktop/DEDA/DEDA/datasets/WorldCup_Winner.xlsx', sheet_name='Tabelle1')

#Read location of Countries
countries = open('C:/Users/VWRZTS0/Desktop/DEDA/DEDA/datasets/countries.csv','r')
countries= countries.readlines()
countries = [i.replace("'","") for i in countries]
countries = [i.replace("\n","") for i in countries]
countries = [i.split(",") for i in countries]
countries = pd.DataFrame(countries)
countries.columns = countries.iloc[0]
countries = countries.drop(0) 
countries = countries.drop(columns={'country'})
countries = countries.rename(columns={'name':'country'})

#participants per WC
wc_participants_h = wcmatches.drop(columns=['Away Team Name','Away Team Goals'])
wc_participants_a = wcmatches.drop(columns=['Home Team Name', 'Home Team Goals'])
wc_participants_h = wc_participants_h.rename(columns={'Home Team Name':'Team','Home Team Goals':'Goals'})
wc_participants_a = wc_participants_a.rename(columns={'Away Team Name':'Team','Away Team Goals':'Goals'})
frames=[wc_participants_h,wc_participants_a]
wc_participants=pd.concat(frames)
wc_participants['Team'] = wc_participants['Team'].replace(['Wales'],'United Kingdom')
wc_participants['Team'] = wc_participants['Team'].replace(['Scotland'],'United Kingdom')
wc_participants['Team'] = wc_participants['Team'].replace(['Northern Ireland'],'United Kingdom')
wc_participants['Team'] = wc_participants['Team'].replace(['England'],'United Kingdom')
wc_participants['Team'] = wc_participants['Team'].replace(['Republic of Ireland'],'Ireland')
wc_participants['Team'] = wc_participants['Team'].replace(['Scotland'],'United Kingdom')
wc_participants['Team'] = wc_participants['Team'].replace(['USA'],'United States')
wc_participants['Team'] = wc_participants['Team'].replace(['Soviet Union'],'Russia')
wc_participants['Team'] = wc_participants['Team'].replace(['Serbia and Montenegro'],'Serbia')
wc_participants['Team'] = wc_participants['Team'].replace(['Korea Republic'],'South Korea')
wc_participants['Team'] = wc_participants['Team'].replace(['Korea DPR'],'Korea')
countries['country'] = countries['country'].replace(['North Korea'],'Korea')
wc_participants['Team'] = wc_participants['Team'].replace(['IR Iran'],'Iran')
wc_participants['Team'] = wc_participants['Team'].replace(['Germany FR'],'Germany')
wc_participants['Team'] = wc_participants['Team'].replace(['German DR'],'Germany')
wc_participants['Team'] = wc_participants['Team'].replace(['China PR'],'China')
wc_participants['Team'] = wc_participants['Team'].replace(['Cï¿½te d\'Ivoire'],'CÃ´te d\'Ivoire')
countries['country'] = countries['country'].replace(['C?te dIvoire'],'CÃ´te d\'Ivoire')
wc_participants['Team'] = wc_participants['Team'].replace(['Czechoslovakia'],'Czech Republic')

wc_participants = wc_participants[wc_participants.Team != "Yugoslavia"]
wc_participants = wc_participants[wc_participants.Team != "Zaire"]
wc_participants = wc_participants[wc_participants.Team != "Dutch East Indies"]

#Add Goals to World Cup participants per Worldcup
goals_stats = wc_participants.groupby(['Year','Team']).Goals.sum().to_frame().reset_index()
goals_stats.insert(3, 'Longitude', goals_stats['Team'].map(countries.set_index('country')['longitude']))
goals_stats.insert(4, 'Latitude', goals_stats['Team'].map(countries.set_index('country')['latitude']))
goals_stats.insert(0, 'ADM0_A3', goals_stats['Team'].map(codes.set_index('Country')['Alpha-3 code']))

#Sum up all World Cup Goals for Each Team
goals_stats_sum = goals_stats.groupby(['Team']).Goals.sum().to_frame().reset_index()
goals_stats_sum.insert(0, 'ADM0_A3', goals_stats_sum['Team'].map(codes.set_index('Country')['Alpha-3 code']))
goals_stats_sum['Goals'] = goals_stats_sum['Goals'].apply(pd.to_numeric)
goals_stats_sum['ADM0_A3'] = goals_stats_sum['ADM0_A3'].astype('str')
goals_stats_sum = goals_stats_sum.drop(columns=['Team'])
 
datafile = goals_stats_sum
shapefile = os.path.expanduser('C:/Users/VWRZTS0/Desktop/DEDA/DEDA/datasets/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp')
 
#Read File in GeoDataFrame   
gdf = gpd.read_file(shapefile)[['ADM0_A3', 'geometry']].to_crs('+proj=robin')
gdf['ADM0_A3'] = gdf['ADM0_A3'].astype('str')

#Merge files
merged_1 = gdf.merge(goals_stats_sum, on='ADM0_A3')
merged_1.describe()

#Set map settings
colors = 8
cmap = 'RdBu_r'
figsize =    (15, 10)
title = 'Sum of all World Cup Goals'
imgfile = 'img/{}.png'.format(title)
description = '''
Sum of all World Cup Goals by Country. • Author: Alexander Munz'''.strip()

#plot figure
ax = merged_1.dropna().plot(column= 'Goals', cmap = cmap, figsize=figsize, scheme='equal_interval', k=colors, legend=True)

merged_1[merged_1.isna().any(axis=1)]

#modify figure
ax.set_title(title, fontdict={'fontsize': 20}, loc='left')
ax.annotate(description, xy=(0.1, 0.1), size=12, xycoords='figure fraction')

#Show figure and save it as png
ax.set_axis_off()
ax.set_xlim([-1.5e7, 1.7e7])
ax.get_legend().set_bbox_to_anchor((.12, .4))
ax.get_figure
fig = ax.get_figure()
fig.savefig("output.png")



