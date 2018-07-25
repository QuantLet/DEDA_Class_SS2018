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
scholars.cleanOrigin()
scholars.addIsActiveColumnInt()
scholars.printScholars(number=2) # number means the number of rows, which shall be printed
scholars.printNumRows()

# request the researcher's geolocation 
scholars.requestGeoDataOSM()    #please execute this function only once and use for further calculations the data from an csv import
scholars.writeCSV(df=scholars.researcher_geo_data, name='geo')
scholars.calculateDistance(lat=52.5189879, long=-13.3925988)
scholars.printResearcherGeoData(number=2)   # number means the number of rows, which shall be printed

# match current and former researcher's interests
scholars.pre_process()
scholars.wordCounts()
scholars.stemTfidf()
scholars.computeCosSimilarity()
scholars.printCosSim()

# compute clusters 
#scholars.prepareClustMatrix()
scholars.elbowMethod(scholars.cosSim)
scholars.computeKMeans(matrix=scholars.cosSim, n=12)
#scholars.computeDbscan()

# TO-DO: evaluate clusters with samples
scholars.printKMeans()
#scholars.plotClusterResults(scholars.kmeans)

# visualize results in a world map
scholars.visualizeGeoCode()

print('--- End Program ---\n')

#MainAnalytics.py    
    