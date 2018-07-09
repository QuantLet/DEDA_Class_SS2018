#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Last Modified on Mon July 07 2018

@author: 
    Natalie

@description: 
    Digital Economy and Decision Analytics
    Project IRTG 1792 Guest Matching 
     
    The text data analytics process contains the steps to gather data, to natural language process the gathered data, to extract features and to apply standard methods. 
    In the following, the author implements the NLP-operations tokenization, filtering,lemmatization to pre-process the gathered data with the function "scrape()".
    

@copyright: 
    

"""
# import custom class 'AnalyseText' to clean data, to pre-process the cleaned data with NLP-operations, to compute DT, LSA (SVD) and clusters as well as manipulate geo data. 
from TextAnalytics.AnalyseText import AnalyseText

print('--- Start Program ---\n')
# initialize dataframe for text analytics operations
scholars = AnalyseText(name='all')

# request and visualize the researcher's location on a world map 
scholars.requestGeoData()
#To-Do: Finish visualization of the geo distribution 
#scholars.visualizeGeoDistribution()

# match current and former researcher's interests
scholars.pre_process()
print(scholars)

dtm = scholars.computeDTM()
dtm_lsa = scholars.computeLSA(dtm)
scholars.printLSAComponent()
scholars.printLSADocuments(dtm_lsa)
scholars.printDocumentSimilarity(dtm_lsa)

# To-Do: rank scholars by their closeness to the IRTG topic using cosine similarity 

print('--- End Program ---\n')

#MainAnalytics.py    
    