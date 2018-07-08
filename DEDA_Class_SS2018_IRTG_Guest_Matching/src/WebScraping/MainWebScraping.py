#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Last Modified on Mon July 07 2018

@author: 
    Natalie

@description: 
    Digital Economy and Decision Analytics
    Project IRTG 1792 Guest Matching 
    
    The first step in the project 'IRTG 1792 Guest Matching' is to retrieve the data about former and current research guests in the IRTG 1792 program from 
    the two websites
        https://www.wiwi.hu-berlin.de/de/forschung/irtg/guests/former-guests
        https://www.wiwi.hu-berlin.de/de/forschung/irtg/guests
    
    Firstly, the function download(url, num_retries) download the HTML-content from the one website and parse the HTML-content to a dataframe respectively
    for former and current researchers. 
    The function concatCurrentFormerDf() concatenates the dataframes of current and former researchers to one dataframe, which is the input of the function
    writeCSV(df, name). The result is one csv-File with all researchers at 'HOME/IRTG/data/researchers_all_[today-data].csv' . 
    
@copyright: 

'''
# import custom webscraping class 'scrape' from WebScraping.scrape
from WebScraping.scrape import scrape

print('--- Start of Web-Scrpaing --- \n')
# url: target website
irtg_former_url = 'https://www.wiwi.hu-berlin.de/de/forschung/irtg/guests/former-guests'
irtg_current_url = 'https://www.wiwi.hu-berlin.de/de/forschung/irtg/guests'

# scrape guest reserachers from wiwi.hu-berlin.de 
print('Start scraping .. \n')
scrp = scrape(current_url=irtg_current_url, former_url=irtg_former_url)
scrp.download(url=scrp.former_url, num_retries=2)
scrp.download(url=scrp.current_url, num_retries=2)

# save scraped data to csv-file
scrp.concatCurrentFormerDf()
scrp.writeCSV(df=scrp.all_researcher_df, name='all')


print('--- End of Web-Scraping. ---')

# MainWebScraping.py
