#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Last Modified on Mon July 07 2018

@author: 
    Natalie

@description: 
    Digital Economy and Decision Analytics
    Project IRTG 1792 Guest Matching 
     
    The text data analytics process contains the steps to gather data, to natural language process the gathered data, to extract features and to apply 
    standard methods. 
    In the following, the author implements the NLP-operations tokenization, filtering,lemmatization to pre-process the gathered data with the function "scrape()".

@copyright: 
    1) Filtering stop words Upadhyay, P.: Removing stop words with NLTK in Python. Under https://www.geeksforgeeks.org/removing-stop-words-nltk-python/ Last Seen July 03, 2018
    2) Filtering punctuation


"""
import pandas as pd     # standard library for machine learning
import numpy as np      # standard library for math
# libraries for NLP
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
# libraries for SVD, LSA and Clustering
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import Normalizer
from sklearn.cluster import KMeans
# library for requesting a location and visualizing the response on a world map 
from geopy.geocoders import Nominatim
# further libraries
#import re   # using regular expressions
import os   # accessing environment of the operating system
from os.path import expanduser  # retrieving the home path 
from datetime import date   # requesting date
from _datetime import timedelta     # calculating time differences 

class AnalyseText:
    
    # data elements of the class AnalyseText
    def __init__(self, name):
        # header of the dataframe researchers ,id,period1,period2,position,origin,interests,isActive
        self.date = date.today()
        self.researchers = self.readCSV(self.getFilePath(name))

        self.researcher_geo_data = self.newResearcherTable()
        
        self.vectorizer = CountVectorizer(min_df=1, stop_words='english')
        self.lsa = TruncatedSVD(n_components=2, algorithm='arpack', n_iter=7)         
    
    # read a CSV-file with the function getFilePath the file path of the scraped content is requested 
    def readCSV(self, filepath):
        researchers = []
        if not filepath:
            raise ValueError('No filepath given')
            return None       
        try:
            researchers = pd.read_csv(filepath_or_buffer = filepath, sep = ',')
        except IOError as e:
            print('IOError', e.message)
            return None   
    
        return researchers
    
    # request for the filepath where the csv-files from the web scraping are stored 
    # note: the csv-files are stored under HOME/IRTG/data   
    def getFilePath(self, name):
        if not(name == 'current' or name == 'former' or name == 'all'):
            print('Wrong name for filepath, please use current, former or all')
            exit
        home = expanduser('~')
        #home = home.replace('\\','/')
        filename = home + '/IRTG/data/' + 'researchers' + '_' + name + '_' + str(self.date) + '.csv'
        filename = os.path.normpath(filename)        
        if os.path.exists(filename):
            return filename
        else:
            return self.getFilePath(self.date-timedelta(1))    
 
    def getCleanedInterests(self):
        return self.researchers.loc[:,'cleanedInterests']
    
    def __str__(self):
        return str(self.researchers.loc[1:4,:])

#############################################################################################
# Clean Data 
#############################################################################################          
    def splitName(self):
        # add new columns surname, forename, startTime, endTime
        self.researchers.loc[:,'surname'] = pd.Series(index=self.researchers.index)
        self.researchers.loc[:,'forename'] = pd.Series(index=self.researchers.index)
        self.researchers.loc[:,'startTime'] = pd.Series(index=self.researchers.index)
        self.researchers.loc[:,'endTime'] = pd.Series(index=self.researchers.index)                
        
        # fill the new columns
        # the surename is in the id column from the beginning of the string until the ','
        # the forename is in the id column after the ',' until the '('
        # the beginning of the time period is in the id column starting with a '(' and ending with a '-'
        # the end of the time period is in the id column starting with a '-' and ending with a ')'
        researcher_index = 0
        for researcher in self.researchers.loc[:,'id']:
            self.researchers.loc[researcher_index, 'surname'] = researcher.split(',',1)[0]
            #self.researchers.loc[researcher_index, 'forename'] = (researcher.split(',',1)[1]).split('(',1)[0]
            #self.researchers.loc[researcher_index, 'startTime'] = (researcher.split('(')[1]).split('-')[0]
            #self.researchers.loc[researcher_index, 'endTime'] = (researcher.split('-')[1]).split(')')[0]
            researcher_index = researcher_index +1

#############################################################################################
# Natural Language Processing 
#############################################################################################   
    def pre_process(self):
        self.researchers.loc[:,'cleanedInterests'] = pd.Series(index=self.researchers.index)
        
        interest_index = 0
        for interest in self.researchers.loc[:,'interests']:
            text_punc = self.filtering_punctuation(str(interest))
            text_lower = self.transform_to_lower(text_punc)
            self.researchers.loc[interest_index,'cleanedInterests'] = self.transform_to_lower(text_lower)
            #text_clean = self.filtering_stop_words(text_stop)
            interest_index = interest_index +1
    
    # Filter stop words 
    def filtering_stop_words(self, one_line):      
        nltk.download('stopwords') 
        nltk.download('punkt') 
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(one_line)
        
        #filtered_line = [w for w in word_tokens if not w in stop_words]
        filtered_line = []
        
        for w in word_tokens:
            if w not in stop_words:
                filtered_line.append(w)
                
        print(filtered_line)
        return filtered_line
        
    # Filter punctuation 
    def filtering_punctuation(self, one_line):
        
        for char in '-.,?!\n\r':
            one_line = one_line.replace(char, ' ')       
        return one_line
    

    # Transfrom words to lower case 
    def transform_to_lower(self, one_line):
        return one_line.lower()
    
    # Lemmatize words assuming each word is a nound (pos = 'n')
    def lemmatize_words(self, one_line):
        nltk.download('wordnet')
        wordnet_lemmatizer = WordNetLemmatizer()

        return wordnet_lemmatizer.lemmatize(one_line)
         
#############################################################################################
# Extract Features - Latent Semantic Analysis using Singular Value Decomposition 
#############################################################################################    

    def computeDTM(self):
        # Compute document-term matrix        
        dtm = self.vectorizer.fit_transform(self.getCleanedInterests())
        # each row represents a document, each column represents a word -> each document is a n-dim vector
        pd.DataFrame(dtm.toarray(), index=self.getCleanedInterests(), columns=self.vectorizer.get_feature_names())
        self.vectorizer.get_feature_names()
        
        return dtm
  
    def computeLSA(self, dtm):
        # Compute SVD and LSA
        dtm = dtm.asfptype()
        dtm_lsa = self.lsa.fit_transform(dtm)
        dtm_lsa = Normalizer(copy=False).fit_transform(dtm_lsa)
        
        return dtm_lsa
   
    def printLSAComponent(self):
        # Each LSA component is a linear combination of words 
        print(pd.DataFrame(self.lsa.components_, index= ['component_1', 'component_2'], columns=self.vectorizer.get_feature_names()))
        print('\n')

    def printLSADocuments(self, dtm_lsa):
        # Each document is a linear combination of the LSA components 
        print(pd.DataFrame(dtm_lsa, index=self.getCleanedInterests(), columns=['component_1', 'component_2']))
        print('\n')    
      
    def printDocumentSimilarity(self, dtm_lsa):
        # Document similarity using LSA components
        similarity = np.asarray(np.asmatrix(dtm_lsa) * np.asmatrix(dtm_lsa).T)
        print(pd.DataFrame(similarity,index=self.getCleanedInterests(),columns=self.getCleanedInterests()).head(10))
        print('\n')    
       
    def clusterComponents(self, dtm_lsa):
        # Use LSA components as features in clustering
        kmeans = KMeans(n_clusters=2, random_state=0).fit(dtm_lsa)  
        
        return kmeans
    

                        
#############################################################################################
# ManipulateGeo
#############################################################################################           
       
    '''
    input: column 'origin' in a dataframe researchers_df
    output: dataframe researcher_geo_df with the columns 'name', 'longtitude', 'latitude', 'country', 'city' -> necessary? -> yes, for clustering 
    generate a new dataframe with the researcher's name as PK and additional columns named in the list/ array 'newHeader'
    '''
    def newResearcherTable(self):
        #'address', 'longtitude', 'latitude'
        newDf = pd.DataFrame(self.researchers.loc[:,'id'])     
        newDf.loc[:,'address'] = pd.Series(index=newDf.index)
        newDf.loc[:,'longtitude'] = pd.Series(index=newDf.index)
        newDf.loc[:,'latitude'] = pd.Series(index=newDf.index)
        return newDf

    # request geo data from OSM by location (column 'origin' with the name of the university)
    def requestGeoData(self):
        #        for researcher in self.researchers.loc[:,'id']:
        print('Start looking up geo data from OSM..')
        origin_index = 0
        for origin in self.researchers.loc[:,'origin']:
            
            geolocator = Nominatim()
            researcher_geo_data = geolocator.geocode(origin)
            if researcher_geo_data: 
                self.researcher_geo_data.loc[origin_index, 'address'] = researcher_geo_data.address
                self.researcher_geo_data.loc[origin_index, 'longtitude'] = researcher_geo_data.latitude
                self.researcher_geo_data.loc[origin_index, 'latitude'] = researcher_geo_data.longitude
            
            origin_index = origin_index +1
            
    # calculate the distance between two researchers
    def calculateDistance(self, researcher_A, researcher_B):
        pass
        
    # present the distribution of the researchers on a world map
    # input df with geo data
    # output html    
    def visualizeGeoDistribution(self):
        pass
              
# AnalyseText.py    
