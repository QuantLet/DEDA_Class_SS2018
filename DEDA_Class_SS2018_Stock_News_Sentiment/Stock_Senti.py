#Import of packages needed
from bs4 import BeautifulSoup
import re
import requests
import pandas as pd
import time
from datetime import datetime
import pandas_datareader.data as data
from pandas_datareader import data
import fix_yahoo_finance as yf

# User inputs
stock         = 'Apple' #input("Stock: ")
symbol        = 'AAPL' #input("Yahoo Finance Symbol: ")

# Retrieve links of articles

article_links = [] # List containing all the article links
tmp_links     = ['1'] # Temporary list to extract the article links per page
i             = 1 # Counter

while tmp_links != []:

    # Create soup using the user input
    base          = 'https://www.finanzen.net'
    html          = requests.get(base + '/news/' + stock + '-News@intpagenr_' + str(i))
    soup          = BeautifulSoup(html.text, "html5lib")

    # Search all news article links on the website
    links         = soup.select('.news-list td')

    # Extract all article links
    tmp_links     = [str(re.findall('href="/nachricht/aktien/.*?"', str(link))[0])[6:-1] for link in links 
                     if re.findall('href="/nachricht/aktien/.*?"', str(link))]
    
    if tmp_links  != []:
        article_links.extend(tmp_links)
        
    print("Downloading links from page " + str(i) + ' - Done')
    i             += 1
    
# Download Article Texts

# Create empty Dictonairy 
doc               = {}
# Set counter
i                 = 1

# Loop to extract articles
for article in article_links:
    # Create temporary soup to extract articles from previous links
    tmp_html      = requests.get(base + article)
    tmp_soup      = BeautifulSoup(tmp_html.text, "html5lib")
    # Search for scripts
    tmp_links     = tmp_soup.find_all('script')
    # Extract the article
    try:
        tmp_stamp               = re.findall('"datePublished":".*?","',str(tmp_links[2]))[0].split('+')[0][17:].split('T')
        tmp_date                = datetime.strptime(str(tmp_stamp[0]), '%Y-%m-%d').date() #tmp_stamp[0]
        tmp_time                = tmp_stamp[1]
        tmp_txt                 = re.findall('"articleBody":".*?;",',str(tmp_links[2]))[0][15:-3]
        doc[tmp_date]           = {}
        doc[tmp_date][tmp_time] = tmp_txt
        print('Downloading article ',i,' out of ',len(article_links),' - Done')
        i += 1
    except:
        print('Downloading article ',i,' out of ',len(article_links)," - Not available")
        i += 1
        
