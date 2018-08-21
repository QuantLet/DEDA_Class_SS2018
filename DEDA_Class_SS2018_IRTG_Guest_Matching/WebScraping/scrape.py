#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Last Modified on Mon July 07 2018

@author: 
    Natalie

@description: 
    Digital Economy and Decision Analytics
    Project IRTG 1792 Guest Matching 

    Algorithm to scrape website in Pseudo-Code 
    input html-text of website former_researchers and current_researchers
    output 
    
    Scrape multiple tables 
    webpage: wiwi.hu-berlin.de/de/researchers/former_researchers
    html_text: downloaded html-code from webpage in text-format 
"""
import requests  # libraries to download websites
from bs4 import BeautifulSoup   # handle html-code
import pandas as pd    # standard library for machine learning
from pandas import DataFrame
# libraries to access operating system information as HOME-path and systemdate
import os
from os.path import expanduser
from datetime import date


class scrape:
    def __init__(self, current_url, former_url):
        # target-websites which are scraped
        self.current_url = current_url
        self.former_url = former_url
        
        # agent for scraping
        self.my_header = {'name': 'natalie.habib@student.hu-berlin.de','user agent': ''}
        self.proxies = None
        
        # dataframes in which the retrieved data is stored 
        self.former_researcher_df = self.getDataFrame()
        self.current_researcher_df = self.getDataFrame()
        self.all_researcher_df = self.getDataFrame()    
        
        # timestamp: current date for history of csv-files
        self.timestamp = date.today()   
        self.path_irtg = self.setHomePath()
           
    def setHomePath(self):
        #build filepath
        # request HOME path
        home = expanduser('~')
        home = home.replace('\\','/')
        path_irtg = home + '/IRTG/data/'
        # build to new directories 
        try:
            if not os.path.exists(path_irtg):
                os.makedirs(path_irtg)
        except OSError:
            pass       
        return path_irtg 


    #download a given url
    #input ..
    #output   
    def download(self, url, num_retries=2, proxies=None):
        print('Downloading: ', url)
        try:
            # resp = requests.get(url, headers=headers, proxies=proxies, timeout=5)
            #    my_header: user agent with name and web-browser
            #    retries: number of retries after timeout 

            resp = requests.get(url, proxies=proxies, timeout=5)
            if resp.status_code >= 400:
                print('Download error: ', resp.text)
                return None
            if num_retries and 500 <= resp.status_code < 600:
                return self.download(url, num_retries -1)
        except requests.exceptions.RequestException as e:
            print('Download error: ', e.reason)
            return None
            
        soup = BeautifulSoup(resp.text, 'lxml')    
                             
        return self.HTML2df(soup, url) 

    #define df_researcher
    #input None
    #column names: [id, position, origin, interests, contact]
    #output empty df 
    def getDataFrame(self):
        return DataFrame(columns=['id', 'period1', 'period2', 'position','origin','interests', 'isActive'])

    #parse a html-text to a df 
    #input html-text of a downloaded website
    #assumption structure of information as described 
    #output df of the website the columns list the variables (1) till (5) without (0) and each row represents 
    #one researcher 
    def HTML2df(self, html_text, url):
        tables = html_text.find_all('table')
        
        if tables is None:
            print('No tables in the html_text found. \n')
            exit
        
        row_marker = 0
        for table in tables:
            df_new_row = self.ParseHTMLTable(table, row_marker)
            if url == self.current_url:
                self.current_researcher_df.loc[row_marker] = df_new_row.loc[row_marker]
                self.current_researcher_df.loc[row_marker, 'isActive'] = True
            else:
                self.former_researcher_df.loc[row_marker] = df_new_row.loc[row_marker]   
                self.former_researcher_df.loc[row_marker, 'isActive'] = False            
            row_marker = row_marker + 1

    #parse one unstructured HTML-table 
    #input HTML-table
    #the table data picture shall be ignored in the scraping process
    #expecting 4 table rows with the variables id, position, origin, and interests
    #in four cases 5 rows with the fifth variable contact 
    #(0)identifying the image file over the img-tag -> ignore it
    #(1)identifying the id over the h5-tag -> save it 
    #(2)identifying the position over the em-tag -> save it 
    #(3)now unique identifier of the origin -> save it
    #(4)identifying interests over the keyword 'Interests' in a td-tag -> save it 
    #(5)identifying contact over the keyword 'Contact' in a td-tag -> ignore it 
    #output: a row for the specified df 
    def ParseHTMLTable(self, data, index):
        # Find table content and save it in a list 
        # Firstly, define variables
        ident = 'NA' # id contains last name, fore name, studying period and mail-address
        position = 'NA'
        origin = 'NA'
        interests = 'NA'
        period1 = 'NA'
        period2 = 'NA'
        isActive = False
        # find all td-tags per table-row and save its content in the defined variables
        for row in data.find_all('tr'):
            
            interest_marker = False        
            for td_tag in row.find_all('td'):
                #(1)identifying the id over the h5-tag -> save it 
                # some scholars have multiple h5-tags with multiple information
                if ident == 'NA':
                    # exception: surename, forname and period is saved in a h2-tag
                    if len(td_tag.find_all('h2')) > 0:
                        ident = self.getContent(td_tag, 'h2')  
                    
                    # case1: the table row includes only one h5-tag -> surename, forname, and timeperiod is saved in one tag
                    if len(td_tag.find_all('h5')) == 1:
                        ident = self.getContent(td_tag, 'h5')
                    else:
                        # case2: the table row includes two or more h5-tag, max are 3 -> surename, forname and two timeperiods are saved in multiple tags 
                        h5_index = 0
                        for h5_tag in td_tag.find_all('h5'):
                            if h5_tag.get_text():
                                if h5_index == 0:
                                    ident = h5_tag.get_text()
                                    
                                elif h5_index == 1:
                                    period1 = h5_tag.get_text()
                                elif h5_index == 2:
                                    period2 = h5_tag.get_text()                                   
                            else:
                                ident = 'NA'
                            h5_index = h5_index+1
                                                                        
                #(2)identifying the position over the em-tag -> save it 
                if position == 'NA':
                    position = self.getContent(td_tag, 'em')
                    
                #(3)no unique identifier of the origin -> save it
                if origin == 'NA':
                    origin = self.getContent(td_tag, 'p')
                
                #(4)identifying interests over the keyword 'Interests' in a td-tag -> save it 
                if interest_marker == True:
                    interests = td_tag.get_text()
                if td_tag.get_text() == "Interests:":
                    interest_marker = True    
        
        # initialize temporary dataframe with the column header 'id','position','origin','interests'
        df_tmp = self.getDataFrame()
        df_tmp.loc[index] = [ident, period1, period2, position, origin, interests, isActive]                        
        return df_tmp

    # returns the content of a html-tag
    # input: td - the table data, from which the content shall be retrieved
    #        ident_tag - the tag, which identify the content (note: the tags on the website have no unique identifier, so that web content is identified by their html-tag
    # output: the content, which is enclosed by the ident_tag 
    #         if the tag is empty, the function will return 'NA'
    def getContent(self, td, ident_tag):
        tag_html = td.find(ident_tag)
        
        # empty string counts as False, all other strings count as True 
        if tag_html is not None:  
            return tag_html.get_text()
        else:
            return 'NA'
    
    # write a given dataframe to a CSV-file at the path HOME/IRTG/data/[name-of-the-file].csv  
    def writeCSV(self, df, name):
        # set path to filename        
        filename_irtg = self.path_irtg + 'researchers' + '_'+ name + '_' + str(self.timestamp) + '.csv'
        
        # export scraped data to csv-file to filename_irtg
        print('Export scraped data to {} .. \n'.format(filename_irtg))               
        if df.empty:
            raise ValueError('DataFrame is empty')        
        try:
            df.to_csv(filename_irtg)
        except IOError as e:
            print('IOError', e.message)
            
    # merge two dataframes df1 and df2        
    def concatCurrentFormerDf(self):
        frames = [self.current_researcher_df, self.former_researcher_df]
        self.all_researcher_df = pd.concat(frames)

#scrape.py
