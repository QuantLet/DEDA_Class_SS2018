# -*- coding: utf-8 -*-
"""
Created on Fri May 25 10:36:16 2018

@author: ivan
"""

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
%matplotlib inline
from PIL import Image

# The following code includes "unknown miner" as a single group (On the second  
# part of the code the "unkown miner" is excluded and the analysis is repeated)

# BITCOIN data loading

# Do no forget to change the current directory
btc = pd.read_csv("BTC.csv", parse_dates=["time"], index_col="time")

btc_pools = btc.resample("M")["guessed_miner"].value_counts()
btc_pools = btc_pools.to_frame()
btc_pools.columns = ["value"]
btc_pools = btc_pools.reset_index()

# BITCOIN CASH data loading
btc_cash = pd.read_csv("BTC cash.csv", parse_dates=["time"], index_col="time")

btc_cash_pools = btc_cash.resample("M")["guessed_miner"].value_counts()
btc_cash_pools = btc_cash_pools.to_frame()
btc_cash_pools.columns = ["value"]
btc_cash_pools = btc_cash_pools.reset_index()

# ETH beta data loading
eth = pd.read_csv("ETH beta.csv", parse_dates=["time"], index_col="time")
eth.index = pd.to_datetime(eth.index,unit='s')

eth_pools = eth.to_period('M').groupby('time')['miner'].value_counts()
#eth_pools = eth.resample("M")["miner"].value_counts()
eth_pools = eth_pools.to_frame()
eth_pools.columns = ["value"]
eth_pools = eth_pools.reset_index()
eth_pools.columns = ["time", "guessed_miner", "value"]
#eth_pools.to_csv("eth_pools")

# LITECOIN data loading
ltc = pd.read_csv("ltc.csv", parse_dates=["unixtime"], index_col="unixtime")
ltc.index = pd.to_datetime(ltc.index,unit='s')
ltc.miner = ltc.miner.fillna("Unknown")

ltc_pools = ltc.resample("M")["miner"].value_counts()
ltc_pools = ltc_pools.to_frame()
ltc_pools.columns = ["value"]
ltc_pools = ltc_pools.reset_index()
ltc_pools.columns = ["time", "guessed_miner", "value"]

# DASH data loading
dash = pd.read_csv("dash.csv", parse_dates=["unixtime"], index_col="unixtime")
dash.index = pd.to_datetime(dash.index,unit='s')
dash.miner = dash.miner.fillna("Unknown")

#dash_pools = dash.to_period('M').groupby('unixtime')['miner'].value_counts()
dash_pools = dash.resample("M")["miner"].value_counts()
dash_pools = dash_pools.to_frame()
dash_pools.columns = ["value"]
dash_pools = dash_pools.reset_index()
dash_pools.columns = ["time", "guessed_miner", "value"]

# GINI CALCULATION

# # Define Gini Formula 
# (according to: https://en.wikipedia.org/wiki/Gini_coefficient, section: Alternate expressions)
def gini(arr):
    ## first sort
    sorted_arr = arr.copy()
    sorted_arr.sort_values()
    n = arr.size
    coef_ = 2. / n
    const_ = (n + 1.) / n
    weighted_sum = sum([(i+1)*yi for i, yi in enumerate(sorted_arr)])
    return coef_*weighted_sum/(sorted_arr.sum()) - const_

# Generate data frame with Gini Index
gini_df = []
for i,j,k,l,m in zip(btc_pools.time.unique(),btc_pools.time.unique(),eth_pools.time.unique(),
                     btc_pools.time.unique(),btc_pools.time.unique()):
    gini_btc = -gini(btc_pools[btc_pools.time == i]["value"])
    gini_btc_cash = -gini(btc_cash_pools[btc_cash_pools.time == j]["value"])
    gini_eth = -gini(eth_pools[eth_pools.time == k]["value"])
    gini_ltc = -gini(ltc_pools[ltc_pools.time == l]["value"])
    gini_dash = -gini(dash_pools[dash_pools.time == m]["value"])
    gini_df.append((i, gini_btc, gini_btc_cash, gini_eth,gini_ltc, gini_dash))
gini_df = pd.DataFrame(gini_df, columns=('time', 'btc', 'bch','eth','ltc','dash'))
gini_df.set_index('time', inplace=True)

# Plot GINI
gini_df["2016":"2018-04"].plot()
plt.savefig('plot1.png', transparent=True)

# Save plot with transparent background
img = Image.open('plot1.png')
img = img.convert("RGBA")
datas = img.getdata()

newData = []
for item in datas:
    if item[0] == 255 and item[1] == 255 and item[2] == 255:
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

img.putdata(newData)
img.save("plot1_trans.png", "PNG")

# Plot Lorenz Curve
btc_lorenz = btc["2016":"2018-04"]["guessed_miner"].value_counts().values
btc_lorenz = np.sort(btc_lorenz)
btc_lorenz = btc_lorenz.cumsum() / btc_lorenz.sum()
btc_lorenz = np.insert(btc_lorenz, 0, 0)
btc_lorenz = pd.DataFrame(btc_lorenz)
btc_lorenz.columns = ["btc"]

bch_lorenz = btc_cash["2016":"2018-04"]["guessed_miner"].value_counts().values
bch_lorenz = np.sort(bch_lorenz)
bch_lorenz = bch_lorenz.cumsum() / bch_lorenz.sum()
bch_lorenz = np.insert(bch_lorenz, 0, 0)
bch_lorenz = pd.DataFrame(bch_lorenz)
bch_lorenz.columns = ["bch"]

eth_lorenz = eth["2016":"2018-04"]["miner"].value_counts().values
eth_lorenz = np.sort(eth_lorenz)
eth_lorenz = eth_lorenz.cumsum() / eth_lorenz.sum()
eth_lorenz = np.insert(eth_lorenz, 0, 0)
eth_lorenz = pd.DataFrame(eth_lorenz)
eth_lorenz.columns = ["eth"]

ltc_lorenz = ltc["2016":"2018-04"]["miner"].value_counts().values
ltc_lorenz = np.sort(ltc_lorenz)
ltc_lorenz = ltc_lorenz.cumsum() / ltc_lorenz.sum()
ltc_lorenz = np.insert(ltc_lorenz, 0, 0)
ltc_lorenz = pd.DataFrame(ltc_lorenz)
ltc_lorenz.columns = ["ltc"]

dash_lorenz = dash["2016":"2018-04"]["miner"].value_counts().values
dash_lorenz = np.sort(dash_lorenz)
dash_lorenz = dash_lorenz.cumsum() / dash_lorenz.sum()
dash_lorenz = np.insert(dash_lorenz, 0, 0)
dash_lorenz = pd.DataFrame(dash_lorenz)
dash_lorenz.columns = ["ltc"]

plt.plot(np.arange(btc_lorenz.size)/(btc_lorenz.size-1), btc_lorenz, label = "btc")
plt.plot(np.arange(bch_lorenz.size)/(bch_lorenz.size-1), bch_lorenz, label = "bch")
plt.plot(np.arange(eth_lorenz.size)/(eth_lorenz.size-1), eth_lorenz, label = "eth")
plt.plot(np.arange(ltc_lorenz.size)/(ltc_lorenz.size-1), ltc_lorenz, label = "ltc")
plt.plot(np.arange(dash_lorenz.size)/(dash_lorenz.size-1), dash_lorenz, label = "dash")
plt.plot([0,1], [0,1], '--', color='black')
plt.legend(loc='best')
plt.savefig('plot9.png', transparent=True)
plt.show()

# Save plot with transparent background
img = Image.open('plot9.png')
img = img.convert("RGBA")
datas = img.getdata()

newData = []
for item in datas:
    if item[0] == 255 and item[1] == 255 and item[2] == 255:
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

img.putdata(newData)
img.save("plot9_trans.png", "PNG")

        
# Data for table of mining pool participation
btc["2016":"2018-04"]["guessed_miner"].value_counts()/np.sum(btc["2016":"2018-04"]["guessed_miner"].value_counts())
btc_cash["2016":"2018-04"]["guessed_miner"].value_counts()/np.sum(btc_cash["2016":"2018-04"]["guessed_miner"].value_counts())
eth["2016":"2018-04"]["miner"].value_counts()/np.sum(eth["2016":"2018-04"]["miner"].value_counts())
ltc["2016":"2018-04"]["miner"].value_counts()/np.sum(ltc["2016":"2018-04"]["miner"].value_counts())
dash["2016":"2018-04"]["miner"].value_counts()/np.sum(dash["2016":"2018-04"]["miner"].value_counts())

# HERFINDAHL HIRSCHMAN INDEX (HHI) CALCULATION

def hhi(arr):
    ## first sort
    sorted_arr = arr.copy()
    sorted_arr.sort_values()
    n = sum(arr)
    squared_sum = sum([(i/n*100)**2 for i in sorted_arr])
    return squared_sum

# Generate data frame with HHI Index
hhi_df = []
for i,j,k,l,m in zip(btc_pools.time.unique(),btc_pools.time.unique(),
                     eth_pools.time.unique(),btc_pools.time.unique(),btc_pools.time.unique()):
    hhi_btc = hhi(btc_pools[btc_pools.time == i]["value"])
    hhi_btc_cash = hhi(btc_cash_pools[btc_cash_pools.time == j]["value"])
    hhi_eth = hhi(eth_pools[eth_pools.time == k]["value"])
    hhi_ltc = hhi(ltc_pools[ltc_pools.time == l]["value"])
    hhi_dash = hhi(dash_pools[dash_pools.time == l]["value"])
    hhi_df.append((i, hhi_btc, hhi_btc_cash, hhi_eth, hhi_ltc, hhi_dash))
hhi_df = pd.DataFrame(hhi_df, columns=('time', 'btc', 'bch', 'eth', "ltc", "dash"))
hhi_df.set_index('time', inplace=True)

# Plots HHI
hhi_df["2016":"2018-04"].plot().legend(loc = "upper left")
plt.savefig('plot3.png', transparent=True)

# Save plot with transparent background
img = Image.open('plot3.png')
img = img.convert("RGBA")
datas = img.getdata()

newData = []
for item in datas:
    if item[0] == 255 and item[1] == 255 and item[2] == 255:
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

img.putdata(newData)
img.save("plot3_trans.png", "PNG")

# Participation of the big 3 (cumulative participation of the 3 most important pools)
np.sum((btc["2016":"2018-04"]["guessed_miner"].value_counts()/np.sum(btc["2016":"2018-04"]["guessed_miner"].value_counts()))[0:3])
np.sum((btc_cash["2016":"2018-04"]["guessed_miner"].value_counts()/np.sum(btc_cash["2016":"2018-04"]["guessed_miner"].value_counts()))[0:3])
np.sum((eth["2016":"2018-04"]["miner"].value_counts()/np.sum(eth["2016":"2018-04"]["miner"].value_counts()))[0:3])
np.sum((ltc["2016":"2018-04"]["miner"].value_counts()/np.sum(ltc["2016":"2018-04"]["miner"].value_counts()))[0:3])
np.sum((dash["2016":"2018-04"]["miner"].value_counts()/np.sum(dash["2016":"2018-04"]["miner"].value_counts()))[0:3])

###############################################################################

# Excluding Unknown Miner
btc_pools2 = btc_pools[btc_pools.guessed_miner != "Unknown"]
btc_cash_pools2 = btc_cash_pools[btc_cash_pools.guessed_miner != "Unknown"] 
eth_pools2 = eth_pools[eth_pools.guessed_miner != "Unknown"] 
ltc_pools2 = ltc_pools[ltc_pools.guessed_miner != "Unknown"] 
dash_pools2 = dash_pools[dash_pools.guessed_miner != "Unknown"] 


# Generate data frame with Gini Index (without unknown miner)
gini_df2 = []
for i,j,k,l,m in zip(btc_pools2.time.unique(),btc_pools2.time.unique(),eth_pools2.time.unique(),
                     btc_pools2.time.unique(),btc_pools2.time.unique()):
    gini_btc = -gini(btc_pools2[btc_pools2.time == i]["value"])
    gini_btc_cash = -gini(btc_cash_pools2[btc_cash_pools2.time == j]["value"])
    gini_eth = -gini(eth_pools2[eth_pools2.time == k]["value"])
    gini_ltc = -gini(ltc_pools2[ltc_pools2.time == l]["value"])
    gini_dash = -gini(dash_pools2[dash_pools2.time == m]["value"])
    gini_df2.append((i, gini_btc, gini_btc_cash, gini_eth,gini_ltc, gini_dash))
gini_df2 = pd.DataFrame(gini_df2, columns=('time', 'btc', 'bch','eth','ltc','dash'))
gini_df2.set_index('time', inplace=True)

# PLOTS GINI (without unknown miner)
gini_df2["2016":"2018-04"].plot()
#plt.savefig('plot2.png', transparent=True)

# Save plot with transparent background
img = Image.open('plot2.png')
img = img.convert("RGBA")
datas = img.getdata()

newData = []
for item in datas:
    if item[0] == 255 and item[1] == 255 and item[2] == 255:
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

img.putdata(newData)
img.save("plot2_trans.png", "PNG")

# Data for table of mining pool participation (exluding unknown miners)
btc[btc.guessed_miner != "Unknown"]["2016":"2018-04"]["guessed_miner"].value_counts()/np.sum(btc[btc.guessed_miner != "Unknown"]["2016":"2018-04"]["guessed_miner"].value_counts())
btc_cash[btc_cash.guessed_miner != "Unknown"]["2016":"2018-04"]["guessed_miner"].value_counts()/np.sum(btc_cash[btc_cash.guessed_miner != "Unknown"]["2016":"2018-04"]["guessed_miner"].value_counts())
eth[eth.miner != "Unknown"]["2016":"2018-04"]["miner"].value_counts()/np.sum(eth[eth.miner != "Unknown"]["2016":"2018-04"]["miner"].value_counts())
ltc[ltc.miner != "Unknown"]["2016":"2018-04"]["miner"].value_counts()/np.sum(ltc[ltc.miner != "Unknown"]["2016":"2018-04"]["miner"].value_counts())
dash[dash.miner != "Unknown"]["2016":"2018-04"]["miner"].value_counts()/np.sum(dash[dash.miner != "Unknown"]["2016":"2018-04"]["miner"].value_counts())

# Generate data frame with HHI Index (without unknown miner)
hhi_df2 = []
for i,j,k,l,m in zip(btc_pools2.time.unique(),btc_pools2.time.unique(),
                     eth_pools2.time.unique(),btc_pools2.time.unique(),btc_pools2.time.unique()):
    hhi_btc = hhi(btc_pools2[btc_pools2.time == i]["value"])
    hhi_btc_cash = hhi(btc_cash_pools2[btc_cash_pools2.time == j]["value"])
    hhi_eth = hhi(eth_pools2[eth_pools2.time == k]["value"])
    hhi_ltc = hhi(ltc_pools2[ltc_pools2.time == l]["value"])
    hhi_dash = hhi(dash_pools2[dash_pools2.time == l]["value"])
    hhi_df2.append((i, hhi_btc, hhi_btc_cash, hhi_eth, hhi_ltc, hhi_dash))
hhi_df2 = pd.DataFrame(hhi_df2, columns=('time', 'btc', 'bch', 'eth', "ltc", "dash"))
hhi_df2.set_index('time', inplace=True)

# Plot HHI
hhi_df2["2016":"2018-04"].plot().legend(loc = "lower left")
#plt.savefig('plot4.png', transparent=True)

# Save plot with transparent background
img = Image.open('plot4.png')
img = img.convert("RGBA")
datas = img.getdata()

newData = []
for item in datas:
    if item[0] == 255 and item[1] == 255 and item[2] == 255:
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

img.putdata(newData)
img.save("plot4_trans.png", "PNG")


# Participation of the big 3 (cumulative participation of the 3 most important pools)
np.sum((btc[btc.guessed_miner != "Unknown"]["2016":"2018-04"]["guessed_miner"].value_counts()/np.sum(btc[btc.guessed_miner != "Unknown"]["2016":"2018-04"]["guessed_miner"].value_counts()))[0:3])
np.sum((btc_cash[btc_cash.guessed_miner != "Unknown"]["2016":"2018-04"]["guessed_miner"].value_counts()/np.sum(btc_cash[btc_cash.guessed_miner != "Unknown"]["2016":"2018-04"]["guessed_miner"].value_counts()))[0:3])
np.sum((eth[eth.miner != "Unknown"]["2016":"2018-04"]["miner"].value_counts()/np.sum(eth[eth.miner != "Unknown"]["2016":"2018-04"]["miner"].value_counts()))[0:3])
np.sum((ltc[ltc.miner != "Unknown"]["2016":"2018-04"]["miner"].value_counts()/np.sum(ltc[ltc.miner != "Unknown"]["2016":"2018-04"]["miner"].value_counts()))[0:3])
np.sum((dash[dash.miner != "Unknown"]["2016":"2018-04"]["miner"].value_counts()/np.sum(dash[dash.miner != "Unknown"]["2016":"2018-04"]["miner"].value_counts()))[0:3])

###############################################################################

# Plots GINI vs Price

# BTC price data loading 
btc_price = pd.read_csv("btc_price.csv", parse_dates=["date"], index_col="date")
btc_price.columns = ["price", "difficulty"]
btc_price = btc_price["2016":"2018-04"]
btc_price.price = btc_price.price.astype(float)
btc_price = btc_price.resample("M").mean()

ax1 = gini_df["2016":"2018-04"]["btc"].plot(label = "btc gini")
ax2 = btc_price["2016":"2018-04"]["price"].plot(label = "price (right axis)", secondary_y=True)
ax1.set_ylim(0, 1)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
plt.legend(h1+h2, l1+l2, loc=2)
#plt.savefig('plot5.png', transparent=True)
plt.show()


# Save plot with transparent background
img = Image.open('plot5.png')
img = img.convert("RGBA")
datas = img.getdata()

newData = []
for item in datas:
    if item[0] == 255 and item[1] == 255 and item[2] == 255:
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

img.putdata(newData)
img.save("plot5_trans.png", "PNG")


# ETH price data loading
eth_price = pd.read_csv("eth_price.csv", parse_dates=["date"], index_col="date")
eth_price.columns = ["price", "difficulty"]
eth_price = eth_price["2016":"2018-04"]
eth_price.price = eth_price.price.astype(float)
eth_price = eth_price.resample("M").mean()

ax1 = gini_df["2016":"2018-04"]["eth"].plot(label = "eth gini")
ax2 = eth_price["2016":"2018-04"]["price"].plot(label = "price (right axis)", secondary_y=True)
ax1.set_ylim(0, 1)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
plt.legend(h1+h2, l1+l2, loc=2)
#plt.savefig('plot6.png', transparent=True)
plt.show()

# Save plot with transparent background
img = Image.open('plot6.png')
img = img.convert("RGBA")
datas = img.getdata()

newData = []
for item in datas:
    if item[0] == 255 and item[1] == 255 and item[2] == 255:
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

img.putdata(newData)
img.save("plot6_trans.png", "PNG")

# LTC price data loading
ltc_price = pd.read_csv("ltc_price.csv", parse_dates=["date"], index_col="date")
ltc_price.columns = ["price", "difficulty"]
ltc_price = ltc_price["2016":"2018-04"]
ltc_price.price = ltc_price.price.astype(float)
ltc_price = ltc_price.resample("M").mean()

ax1 = gini_df["2016":"2018-04"]["ltc"].plot(label = "ltc gini")
ax2 = ltc_price["2016":"2018-04"]["price"].plot(label = "price (right axis)", secondary_y=True)
ax1.set_ylim(0, 1)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
plt.legend(h1+h2, l1+l2, loc=2)
#plt.savefig('plot7.png', transparent=True)
plt.show()

# Save plot with transparent background
img = Image.open('plot7.png')
img = img.convert("RGBA")
datas = img.getdata()

newData = []
for item in datas:
    if item[0] == 255 and item[1] == 255 and item[2] == 255:
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

img.putdata(newData)
img.save("plot7_trans.png", "PNG")


# DASH price data loading
dash_price = pd.read_csv("dash_price.csv", parse_dates=["date"], index_col="date")
dash_price.columns = ["price", "difficulty"]
dash_price = dash_price["2016":"2018-04"]
dash_price.price = dash_price.price.astype(float)
dash_price = dash_price.resample("M").mean()

ax1 = gini_df["2016":"2018-04"]["dash"].plot(label = "dash_gini")
ax2 = dash_price["2016":"2018-04"]["price"].plot(label = "price (right axis)",secondary_y=True)
ax1.set_ylim(0, 1)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
plt.legend(h1+h2, l1+l2, loc=2)
#plt.savefig('plot8.png', transparent=True)
plt.show()

# Save plot with transparent background
img = Image.open('plot8.png')
img = img.convert("RGBA")
datas = img.getdata()

newData = []
for item in datas:
    if item[0] == 255 and item[1] == 255 and item[2] == 255:
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

img.putdata(newData)
img.save("plot8_trans.png", "PNG")

###############################################################################

# Plots HHI vs Price

# BTC
ax1 = hhi_df["2016":"2018-04"]["btc"].plot(label = "btc HHI")
ax2 = btc_price["2016":"2018-04"]["price"].plot(secondary_y=True)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
plt.legend(h1+h2, l1+l2, loc=2)
plt.savefig('plot10.png', transparent=True)
plt.show()

# Save plot with transparent background
img = Image.open('plot10.png')
img = img.convert("RGBA")
datas = img.getdata()

newData = []
for item in datas:
    if item[0] == 255 and item[1] == 255 and item[2] == 255:
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

img.putdata(newData)
img.save("plot10_trans.png", "PNG")


# ETH
ax1 = hhi_df["2016":"2018-04"]["eth"].plot(label = "eth HHI")
ax2 = eth_price["2016":"2018-04"]["price"].plot(secondary_y=True)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
plt.legend(h1+h2, l1+l2, loc=2)
plt.savefig('plot11.png', transparent=True)
plt.show()

# Save plot with transparent background
img = Image.open('plot11.png')
img = img.convert("RGBA")
datas = img.getdata()

newData = []
for item in datas:
    if item[0] == 255 and item[1] == 255 and item[2] == 255:
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

img.putdata(newData)
img.save("plot11_trans.png", "PNG")

# LTC
ax1 = hhi_df["2016":"2018-04"]["ltc"].plot(label = "ltc HHI")
ax2 = ltc_price["2016":"2018-04"]["price"].plot(secondary_y=True)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
plt.legend(h1+h2, l1+l2, loc=2)
plt.savefig('plot12.png', transparent=True)
plt.show()

# Save plot with transparent background
img = Image.open('plot12.png')
img = img.convert("RGBA")
datas = img.getdata()

newData = []
for item in datas:
    if item[0] == 255 and item[1] == 255 and item[2] == 255:
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

img.putdata(newData)
img.save("plot12_trans.png", "PNG")

# DASH
ax1 = hhi_df["2016":"2018-04"]["dash"].plot(label = "dash HHI")
ax2 = dash_price["2016":"2018-04"]["price"].plot(secondary_y=True)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
plt.legend(h1+h2, l1+l2, loc=2)
plt.savefig('plot13.png', transparent=True)
plt.show()

# Save plot with transparent background
img = Image.open('plot13.png')
img = img.convert("RGBA")
datas = img.getdata()

newData = []
for item in datas:
    if item[0] == 255 and item[1] == 255 and item[2] == 255:
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

img.putdata(newData)
img.save("plot13_trans.png", "PNG")

###############################################################################

# Plots HHI vs difficulty

# BTC
ax1 = hhi_df["2016":"2018-04"]["btc"].plot()
ax2 = btc_price["2016":"2018-04"]["difficulty"].plot(secondary_y=True)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
plt.legend(h1+h2, l1+l2, loc=2)
plt.show()

# ETH
ax1 = hhi_df["2016":"2018-04"]["eth beta"].plot()
ax2 = eth_price["2016":"2018-04"]["difficulty"].plot(secondary_y=True)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
plt.legend(h1+h2, l1+l2, loc=2)
plt.show()

# LTC
ax1 = hhi_df["2016":"2018-04"]["ltc"].plot()
ax2 = ltc_price["2016":"2018-04"]["difficulty"].plot(secondary_y=True)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
plt.legend(h1+h2, l1+l2, loc=2)
plt.show()

# DASH
ax1 = hhi_df["2016":"2018-04"]["dash"].plot()
ax2 = dash_price["2016":"2018-04"]["difficulty"].plot(secondary_y=True)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
plt.legend(h1+h2, l1+l2, loc=2)
plt.show()

###############################################################################

# VAR model
import statsmodels.api as sm
from statsmodels.tsa.api import VAR, DynamicVAR
from statsmodels.tsa.base.datetools import dates_from_str

# Prepare data for the VAR model
datavar = hhi_df[0:]
datavar.columns = ["btc hhi", "bch hhi", "eth hhi", "ltc hhi","dash hhi"]
datavar.insert(loc = 5, column = "btc price", value = btc_price.price)
datavar.insert(loc = 6, column = "eth price", value = eth_price.price)
datavar.insert(loc = 7, column = "ltc price", value = ltc_price.price)
datavar.insert(loc = 8, column = "dash price", value = dash_price.price)

# VAR model for BTC
datavar1 = datavar[['btc hhi','btc price']]
datavar1 = np.log(datavar1).diff().dropna()
model1 = VAR(datavar1)
results1 = model1.fit(2)
results1.summary()

# VAR model for BTC in 2017 - 2018
datavar2 = datavar[['btc hhi','btc price']]["2017"]
datavar2 = np.log(datavar2).diff().dropna()
model2 = VAR(datavar2)
results2 = model2.fit(2)
results2.summary()
