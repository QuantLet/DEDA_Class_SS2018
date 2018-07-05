# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 21:10:23 2018

@author: AlexMunz
"""

import pandas as pd
from  plotly.offline import plot

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
codes = codes.drop_duplicates(subset='Country')

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
wc_participants['Team'] = wc_participants['Team'].replace(['Korea DPR'],'South Korea')
countries['country'] = countries['country'].replace(['North Korea'],'South Korea')
wc_participants['Team'] = wc_participants['Team'].replace(['IR Iran'],'Iran')
wc_participants['Team'] = wc_participants['Team'].replace(['Germany FR'],'Germany')
wc_participants['Team'] = wc_participants['Team'].replace(['German DR'],'Germany')
wc_participants['Team'] = wc_participants['Team'].replace(['China PR'],'China')
wc_participants['Team'] = wc_participants['Team'].replace(['Cï¿½te d\'Ivoire'],'CÃ´te d\'Ivoire')
countries['country'] = countries['country'].replace(['C?te dIvoire'],'CÃ´te d\'Ivoire')
wc_participants['Team'] = wc_participants['Team'].replace(['Czechoslovakia'],'Czech Republic')

#Delete countries from DataFrame which we have no data for
wc_participants = wc_participants[wc_participants.Team != "Yugoslavia"]
wc_participants = wc_participants[wc_participants.Team != "Zaire"]
wc_participants = wc_participants[wc_participants.Team != "Dutch East Indies"]

#Sum up Goals by Team for each World Cup
goals_stats = wc_participants.groupby(['Year','Team']).Goals.sum().to_frame().reset_index()

#Sum up overall Goals per Team
goals_stats_sum = goals_stats.groupby(['Team']).Goals.sum().to_frame().reset_index()
goals_stats_sum.insert(0, 'ADM0_A3', goals_stats_sum['Team'].map(codes.set_index('Country')['Alpha-3 code']))
goals_stats_sum['Goals'] = goals_stats_sum['Goals'].apply(pd.to_numeric)
goals_stats_sum['ADM0_A3'] = goals_stats_sum['ADM0_A3'].astype('str')

#List all Teams
allteams = list(goals_stats_sum['Team'])
allteamsyears = allteams * 20

# Include wcvears Series to DataFrame
wcyears =[]
for i in range(len(allteams)):
    wcyears.append('1930')
for i in range(len(allteams)):
    wcyears.append('1934')
for i in range(len(allteams)):
    wcyears.append('1938')
for i in range(len(allteams)):
    wcyears.append('1950')
for i in range(len(allteams)):
    wcyears.append('1954')
for i in range(len(allteams)):
    wcyears.append('1958')
for i in range(len(allteams)):
    wcyears.append('1962')
for i in range(len(allteams)):
    wcyears.append('1966')
for i in range(len(allteams)):
    wcyears.append('1970')
for i in range(len(allteams)):
    wcyears.append('1974')
for i in range(len(allteams)):
    wcyears.append('1978')
for i in range(len(allteams)):
    wcyears.append('1982')
for i in range(len(allteams)):
    wcyears.append('1986')  
for i in range(len(allteams)):
    wcyears.append('1990')
for i in range(len(allteams)):
    wcyears.append('1994')
for i in range(len(allteams)):
    wcyears.append('1998')
for i in range(len(allteams)):
    wcyears.append('2002')
for i in range(len(allteams)):
    wcyears.append('2006')
for i in range(len(allteams)):
    wcyears.append('2010')
for i in range(len(allteams)):
    wcyears.append('2014')
wcyears=pd.Series(wcyears) 
new_data=pd.DataFrame(wcyears)
new_data.columns = ['Year']

#include Teams to DataFrame
allteamsyears = pd.Series(allteamsyears)
new_data['Team'] = allteamsyears

#Merge DataFrame
df = pd.merge(new_data,goals_stats, on=['Year','Team'])

#Fill DataFrame with missing rows so that all countries are included for all World Cups
iterables = [df['Year'].unique(),df['Team'].unique()]
new_df = df.set_index(['Year','Team'])
new_df = new_df.reindex(index=pd.MultiIndex.from_product(iterables, names=['Year', 'Team']), fill_value=0).reset_index()

new_df.insert(0, 'ADM0_A3', new_df['Team'].map(codes.set_index('Country')['Alpha-3 code']))


#Specify datasets for each Worldcup
data1930 = new_df.loc[:69]
data1934 = new_df.loc[70:139]
data1938 = new_df.loc[140:209]
data1950 = new_df.loc[210:279]
data1954 = new_df.loc[280:349]
data1958 = new_df.loc[350:419]
data1962 = new_df.loc[420:489]
data1966 = new_df.loc[490:559]
data1970 = new_df.loc[560:629]
data1974 = new_df.loc[630:699]
data1978 = new_df.loc[700:769]
data1982 = new_df.loc[770:839]
data1986 = new_df.loc[840:909]
data1990 = new_df.loc[910:979]
data1994 = new_df.loc[980:1049]
data1998 = new_df.loc[1050:1119]
data2002 = new_df.loc[1120:1189]
data2006 = new_df.loc[1190:1259]
data2010 = new_df.loc[1260:1329]
data2014 = new_df.loc[1330:1399]

#Define Choroplath map that are going to be plotted
data=[]

data1 =  dict(
        type = 'choropleth',
        locations = data1930['ADM0_A3'],
        z = data1930['Goals'],
        text = data1930['Team'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5) ),
        colorbar = dict(title = 'Goals 1930')
      ) 

data.append(data1)       

data2 =  dict(
        type = 'choropleth',
        locations = data1934['ADM0_A3'],
        z = data1934['Goals'],
        text = data1934['Team'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5) ),
        colorbar = dict(title = 'Goals 1934'),
        ) 

data.append(data2) 

data3 = dict(
        type = 'choropleth',
        locations = data1938['ADM0_A3'],
        z = data1938['Goals'],
        text = data1938['Team'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(title = 'Goals 1938'),
      ) 

data.append(data3)
         
data4 = dict(
        type = 'choropleth',
        locations = codes['Alpha-3 code'],
        z = 0,
        text = codes['Country'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(title = 'Goals 1942'),
      )

data.append(data4)
      
data5 = dict(
        type = 'choropleth',
        locations = codes['Alpha-3 code'],
        z = 0,
        text = codes['Country'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(title = 'Goals 1946'),
      )

data.append(data5)

data6 = dict(
        type = 'choropleth',
        locations = data1950['ADM0_A3'],
        z = data1950['Goals'],
        text = data1950['Team'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(title = 'Goals 1950'),
      )
        
data.append(data6)       

data7 = dict(
        type = 'choropleth',
        locations = data1954['ADM0_A3'],
        z = data1954['Goals'],
        text = data1954['Team'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(title = 'Goals 1954'),
      )

data.append(data7)

data8 = dict(
        type = 'choropleth',
        locations = data1958['ADM0_A3'],
        z = data1958['Goals'],
        text = data1958['Team'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(title = 'Goals 1958'),
      )

data.append(data8)
           
data9 = dict(
        type = 'choropleth',
        locations = data1962['ADM0_A3'],
        z = data1962['Goals'],
        text = data1962['Team'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(title = 'Goals 1962'),
      )

data.append(data9)
        
data10= dict(
        type = 'choropleth',
        locations = data1966['ADM0_A3'],
        z = data1966['Goals'],
        text = data1966['Team'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(title = 'Goals 1966'),
      )

data.append(data10)       

data11= dict(
        type = 'choropleth',
        locations = data1970['ADM0_A3'],
        z = data1970['Goals'],
        text = data1970['Team'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(title = 'Goals 1970'),
      )

data.append(data11)

data12= dict(
        type = 'choropleth',
        locations = data1974['ADM0_A3'],
        z = data1974['Goals'],
        text = data1974['Team'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(title = 'Goals 1974'),
      )

data.append(data12)           

data13 = dict(
        type = 'choropleth',
        locations = data1978['ADM0_A3'],
        z = data1978['Goals'],
        text = data1978['Team'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(title = 'Goals 1978'),
      )

data.append(data13)       

data14 =  dict(
        type = 'choropleth',
        locations = data1982['ADM0_A3'],
        z = data1982['Goals'],
        text = data1982['Team'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(title = 'Goals 1982'),
      ) 

data.append(data14)

data15 =  dict(
        type = 'choropleth',
        locations = data1986['ADM0_A3'],
        z = data1986['Goals'],
        text = data1986['Team'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(title = 'Goals 1986'),
      ) 

data.append(data15)      

data16 =  dict(
        type = 'choropleth',
        locations = data1990['ADM0_A3'],
        z = data1990['Goals'],
        text = data1990['Team'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(title = 'Goals 1990'),
      ) 

data.append(data16)

data17 =  dict(
        type = 'choropleth',
        locations = data1994['ADM0_A3'],
        z = data1994['Goals'],
        text = data1994['Team'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(title = 'Goals 1994'),
      ) 

data.append(data17)
          
data18 =  dict(
        type = 'choropleth',
        locations = data1998['ADM0_A3'],
        z = data1998['Goals'],
        text = data1998['Team'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(title = 'Goals  1998'),
      ) 

data.append(data18)        

data19 =  dict(
        type = 'choropleth',
        locations = data2002['ADM0_A3'],
        z = data2002['Goals'],
        text = data2002['Team'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(title = 'Goals 2002'),
      ) 

data.append(data19)

data20 =  dict(
        type = 'choropleth',
        locations = data2006['ADM0_A3'],
        z = data2006['Goals'],
        text = data2006['Team'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(title = 'Goals 2006'),
      ) 

data.append(data20)

data21 = dict(
        type = 'choropleth',
        locations = data2010['ADM0_A3'],
        z = data2010['Goals'],
        text = data2010['Team'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(title = 'Goals 2010'),
      ) 

data.append(data21)

data22 = dict(
        type = 'choropleth',
        locations = data2014['ADM0_A3'],
        z = data2014['Goals'],
        text = data2014['Team'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        visible = False,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(title = 'Goals 2014'),
      ) 

data.append(data22)

#Define Dropdown Menu        
updatemenus = list([
    dict(active=0,
         buttons=list([
                 
            dict(label = 'Before World Cups',
                 method = 'style',
                 args = [{'visible': [False,False,False,False,False,False,False,
                                      False,False, False,False,False,False,
                                      False,False,False,False,False,False,
                                      False,False, False,False]},
                         {'title': 'Before 1930'}]),
           dict(label = '1930',
                 method = 'restyle',
                 args = [{'visible': [True,False,False,False,False,False,
                                      False,False, False,False,False,False,
                                      False,False,False,False,False,False,
                                      False,False, False,False]},
                         {'title': '1930'}]),
            dict(label = '1934',
                 method = 'restyle',
                 args = [{'visible': [False,True,False,False,False,False,
                                      False,False, False,False,False,False,
                                      False,False,False,False,False, False,
                                      False,False, False,False]},
                         {'title': '1934'}]),
            dict(label = '1938',
                 method = 'restyle',
                 args = [{'visible': [False,False,True,False,False,False,
                                      False,False, False,False,False,False,
                                      False,False,False,False,False, False,
                                      False,False, False,False]},
                         {'title': '1938'}]),
            dict(label = '1942',
                 method = 'restyle',
                 args = [{'visible': [False,False,False,True,False,
                                      False,False, False,False,False,False,
                                      False,False,False,False,False, False,
                                      False,False, False,False]},
                         {'title': '1942'}]),
           dict(label = '1946',
                 method = 'restyle',
                 args = [{'visible': [False,False,False,False,True,False,
                                      False,False, False,False,False,False,
                                      False,False,False,False,False, False,
                                      False,False, False,False]},
                         {'title': '1946'}]),  
            dict(label = '1950',
                 method = 'restyle',
                 args = [{'visible': [False, False,False,False,False,True,
                                      False,False, False,False,False,False,
                                      False,False,False, False,False, False,
                                      False,False, False, False]},
                         {'title': '1950'}]),
            dict(label = '1954',
                 method = 'restyle',
                 args = [{'visible': [False, False,False,False,False,False,
                                      True,False, False,False,False,False,
                                      False,False,False, False,False, False,
                                      False,False, False, False]},
                         {'title': '1954'}]),
            dict(label = '1958',
                 method = 'restyle',
                 args = [{'visible': [False, False,False,False,False, False,
                                      False,True, False,False,False,False,
                                      False,False,False, False,False, False,
                                      False,False, False, False]},
                         {'title': '1958'}]),
            dict(label = '1962',
                 method = 'restyle',
                 args = [{'visible': [False, False,False,False,False, False,
                                      False,False,True,False,False,False,
                                      False,False,False, False,False, False,
                                      False,False, False, False]},
                         {'title': '1962'}]),  
            dict(label = '1966',
                 method = 'restyle',
                 args = [{'visible': [False, False,False,False,False, False,
                                      False,False,False,True,False,False,
                                      False,False,False, False,False, False,
                                      False,False, False, False]},
                         {'title': '1966'}]),
            dict(label = '1970',
                 method = 'restyle',
                 args = [{'visible': [False, False,False,False,False, False,
                                      False,False, False,True,False,False,
                                      False,False,False, False,False, False,
                                      False,False, False, False]},
                         {'title': '1970'}]),
            dict(label = '1974',
                 method = 'restyle',
                 args = [{'visible': [False, False,False,False,False, False,
                                      False,False, False,False,False,True,
                                      False,False,False, False,False, False,
                                      False,False, False, False]},
                         {'title': '1974'}]),
            dict(label = '1978',
                 method = 'restyle',
                 args = [{'visible': [False, False,False,False,False, False,
                                      False,False, False,False,False,False,
                                      True,False,False, False,False, False,
                                      False,False, False, False]},
                         {'title': '1978',
                          'annotations': []}]),
            dict(label = '1982',
                 method = 'restyle',
                 args = [{'visible': [False, False,False,False, False,
                                      False,False, False,False,False,False,
                                      False,True,False, False,False, False,
                                      False,False, False, False]},
                         {'title': '1982',
                          'annotations': []}]),
            dict(label = '1986',
                 method = 'restyle',
                 args = [{'visible': [False, False,False,False,False, False,
                                      False,False, False,False,False,False,
                                      False,False,True,False,False, False,
                                      False,False, False, False]},
                         {'title': '1986',
                          'annotations': []}]),
            dict(label = '1990',
                 method = 'restyle',
                 args = [{'visible': [False, False,False,False,False, False,
                                      False,False, False,False,False,False,
                                      False,False,False,True,False, False,
                                      False,False, False, False]},
                         {'title': '1990',
                          'annotations': []}]),  
            dict(label = '1994',
                 method = 'restyle',
                 args = [{'visible': [False, False,False,False,False, False,
                                      False,False, False,False,False,False,
                                      False,False,False, False,True, False,
                                      False,False, False, False]},
                         {'title': '1994',
                          'annotations': []}]),
            dict(label = '1998',
                 method = 'restyle',
                 args = [{'visible': [False, False,False,False,False, False,
                                      False,False, False,False,False,False,
                                      False,False,False, False,False, True,
                                      False,False, False, False]},
                         {'title': '1998',
                          'annotations': []}]),
            dict(label = '2002',
                 method = 'restyle',
                 args = [{'visible': [False, False,False,False,False, False,
                                      False,False, False,False,False,False,
                                      False,False,False, False,False, False,
                                      True,False, False, False]},
                         {'title': '2002',
                          'annotations': []}]),
            dict(label = '2006',
                 method = 'restyle',
                 args = [{'visible': [False, False,False,False,False, False,
                                      False,False, False,False,False,False,
                                      False,False,False, False,False, False,
                                      False,True, False, False]},
                         {'title': '2006',
                          'annotations': []}]),
            dict(label = '2010',
                 method = 'restyle',
                 args = [{'visible': [False, False,False,False,False, False,
                                      False,False, False,False,False,False,
                                      False,False,False, False,False, False,
                                      False,False,True, False]},
                         {'title': '2010',
                          'annotations': []}]),
            dict(label = '2014',
                 method = 'restyle',
                 args = [{'visible': [False, False,False,False,False, False,
                                      False,False, False,False,False,False,
                                      False,False,False, False,False, False,
                                      False,False,False,True]},
                         {'title': '2014',
                          'annotations': []}]),
                    ]),
    )
])

#Set layout for plotting
layout = dict(title='WorldCup Goals per Team', showlegend=False,
              updatemenus=updatemenus)

#Define data and layout for the fig and plot fig
fig = dict(data=data, layout=layout)
plot(fig, filename='update_dropdown.html')
