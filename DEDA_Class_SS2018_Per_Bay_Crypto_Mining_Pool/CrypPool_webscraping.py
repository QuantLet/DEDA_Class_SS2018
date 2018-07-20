# -*- coding: utf-8 -*-
"""
Created on Mon May 21 12:56:02 2018

@author: ivan
"""

import requests
from bs4 import BeautifulSoup
import time

## ------
# EXAMPLE
# -------

# Erase the ''' to acttivate the lines for the example:
'''
url = "https://bitcoinchain.com/block_explorer/400"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
stat_table = soup.find_all('table', class_ = 'table table-hover b-blocks__table')[0]
print(stat_table.text)

datasaved = "delete"
for row in stat_table.find_all("tr"):
    data = ""
    for cell in row.find_all("td"):
        data = data + "," + cell.get_text(strip=True).replace(",","")
    datasaved = datasaved + data + "\n"
print(datasaved)
'''

# --------------------
# CODE TO GET THE DATA
# --------------------

# 2017 blocks are those in pages 215:780, so range should be range(215,780)
start = time.time()
for i in range(780,1329):
    url = "https://bitcoinchain.com/block_explorer/{}".format(i)
    time.sleep(2)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    stat_table = soup.find_all('table', class_ = 'table table-hover b-blocks__table')[0]
    
    datasaved = "delete"
    with open ("bitcoinchain.csv", "a") as r:
        #r.write(header)
        for row in stat_table.find_all("tr"):
            data = ""
            for cell in row.find_all("td"):
                data = data + "," + cell.get_text(strip=True).replace(",","")
            datasaved = datasaved + data + "\n"
        r.write(datasaved)
        r.write("\n")
elapsed_time = time.time() - start
time.strftime("%H:%M:%S", time.gmtime(elapsed_time))

    



        
