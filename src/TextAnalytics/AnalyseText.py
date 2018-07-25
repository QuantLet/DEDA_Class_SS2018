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
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import *
#from nltk.stem.snowball import SnowballStemmer

# libraries for SVD, LSA and Clustering
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import Normalizer
from sklearn.cluster import KMeans
from sklearn import metrics
from sklearn.cluster import SpectralClustering
from sklearn.cluster import DBSCAN
from scipy.spatial.distance import cdist

#libraries to plot clusters
import matplotlib.pyplot as plt
#import plotly.plotly as py
#import plotly.graph_objs as go

# library for requesting a location and visualizing the response on a world map 
from geopy.geocoders import Nominatim
from geopy import distance
import folium

# further libraries
#import re   # using regular expressions
import os   # accessing environment of the operating system
from os.path import expanduser  # retrieving the home path 
from datetime import date   # requesting date
from _datetime import timedelta     # calculating time differences 
import time
from sklearn.cluster.tests.test_affinity_propagation import n_clusters



class AnalyseText:
    
    # data elements of the class AnalyseText
    # date:
    #    current date without exact time in the format YYYY-MM-DD
    # researchers:
    #    pandas dataframe, which stores the IRTGS former and current researchers 
    #    header of the dataframe researchers ,id,period1,period2,position,origin,interests,isActive
    #    the dataelement is filled by reading the CSV from the webscraping part by first calling the function getFilePath() and giving the
    #    file path name as input of the function readCSV()
    def __init__(self, name):
        self.date = date.today()
        self.researchers = self.readCSV(self.getFilePath(name, date.today()))
        self.num_rows = self.researchers.shape[0]
        self.researcher_geo_data = self.newResearcherTable()
        #self.researcher_geo_data = self.readCSV(self.getFilePath('geo', date.today()))
        
        self.vectorizer = CountVectorizer(min_df=1, stop_words='english')
        #self.tfidfVectorizer = TfidfVectorizer(tokenizer=self.LemNormalize(), stop_words='english')
        self.lsa = TruncatedSVD(n_components=2, algorithm='arpack', n_iter=7)         
        
        self.X = []
        self.cosSim = []
        self.specClust = []
        self.kmeans = []
        self.dbscanClust = []
        
        # timestamp: current date for history of csv-files
        self.timestamp = date.today()   
        self.path_irtg = self.setHomePath()
    
    # request for the filepath where the csv-files from the web scraping are stored 
    # note: the csv-files are stored under HOME/IRTG/data   
    def getFilePath(self, name, date):
        if not(name == 'current' or name == 'former' or name == 'all' or name == 'geo'):
            print('Wrong name for filepath, please use current, former, all or geo')
            exit
        home = expanduser('~')
        #home = home.replace('\\','/')
        filename = home + '/IRTG/data/' + 'researchers' + '_' + name + '_' + str(date) + '.csv'
        filename = os.path.normpath(filename)        
        if os.path.exists(filename):
            return filename
        else:
            date_previous = date-timedelta(1)
            return self.getFilePath(name, date_previous)    
        
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
 
    # access cleaned interest data from the dataframe researchers
    def getCleanedInterests(self):
        return self.researchers.loc[:,'cleanedInterests']

    # access raw interest data from the dataframe researchers    
    def getRawInterests(self):
        return self.researchers.loc[:,'interests']
    
    # print the first [number] rows of the dataframe 'researchers'
    def printScholars(self, number):
        shape = self.researchers.shape
        print('Summary of the dataframe of the researchers:\n Number of rows(number of total researchers), Number of columns (attributes of the researchers): {}\n{}'.format(shape, self.researchers.loc[1:number,:]))
    
    # for calculation of the tf-idf matrix set a tfidf-vector
    def setTfidfVectorizer(self):
        tf = TfidfVectorizer(analyzer='word')
        txt_fitted = tf.fit(self.getRawInterests())
        txt_transformed = txt_fitted.transform(self.getRawInterests())
        
        return txt_transformed

    # write a given dataframe to a CSV-file at the path HOME/IRTG/data/[name-of-the-file].csv  
    def writeCSV(self, df, name):
        # set path to filename        
        filename_irtg = self.path_irtg + 'researchers' + '_'+ name + '_' + str(self.timestamp) + '.csv'
        
        # export scraped data to csv-file to filename_irtg
        print('Export data to {} .. \n'.format(filename_irtg))               
        if df.empty:
            raise ValueError('DataFrame is empty')        
        try:
            df.to_csv(filename_irtg)
        except IOError as e:
            print('IOError', e.message)       

    # add a new column, in which the state of the researcher (active or not active) is numerized 
    def addIsActiveColumnInt(self):
        self.researchers.loc[:,'isActive_int'] = ""
        state_index = 0
        for state in self.researchers.loc[:,'isActive']:
            if state == True:
                self.researchers.loc[state_index, 'isActive_int'] = 1
            else:
                self.researchers.loc[state_index, 'isActive_int'] = 0
            state_index = state_index + 1 
            
    def printNumRows(self):
        print(self.num_rows)
        
    # print any array to check its content           
    def printArray(self, clustX):
        for i in range(len(clustX)):
            print(clustX[i])
 

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
            
    def cleanOrigin(self):
        researcher_index = 0       
        for origin in self.researchers.loc[:,'origin']:
            if type(origin) != str:
                self.researchers.loc[researcher_index,'origin'] = 'Humboldt University Berlin'
            print(self.researchers.loc[researcher_index,'origin'])
            researcher_index = researcher_index +1
            
            
#############################################################################################
# Natural Language Processing 
#############################################################################################   
    # function to pre-process the given interests of the scholars of one entity of the class MainAnalytics()
    # Therefore, add a new column, in which punctuation and stop words-filtered, lowered-cased, and lemmatized interest words as tokens are stored
    # input: 
    #    none, function works on the dataframe-object 'researchers' of the class 
    # output: 
    #    new column 'cleanedInterests' with the pre-processed interest data 
    # libraries and dictionaries:
    #    nltk, wordnet 
    def pre_process(self):
        # add a new empty column 'cleanedInterests' to the data frame to not work on the original interst data
        self.researchers.loc[:,'cleanedInterests'] = ""      
        
        # download dictionaries
        nltk.download('stopwords') 
        nltk.download('punkt') 
        nltk.download('wordnet')         
        
        # pre-process each line (one interest) in a for-loop 
        # and store the pre-processed interest data in the new column 'cleanedInterest'
        interest_index = 0
        for interest in self.researchers.loc[:,'interests']:
            # pre-process
            text_punc = self.filtering_punctuation(str(interest))
            text_lower = self.transform_to_lower(text_punc)
            #text_stop = self.filtering_stop_words(text_lower)
            #text_clean = self.stemming_words(text_stop)
            
            # store pre-processed interest data 
            self.researchers.at[interest_index,'cleanedInterests'] = text_lower
            interest_index = interest_index +1
    
    # Filter stop words 
    def filtering_stop_words(self, one_line):      
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(one_line)
        
        #filtered_line = [w for w in word_tokens if not w in stop_words]
        filtered_line = []
        for w in word_tokens:
            if w not in stop_words:
                filtered_line.append(w)
                
        return filtered_line
        
    # Filter punctuation 
    def filtering_punctuation(self, one_line):        
        for char in '-.,?!\n\r&/':
            one_line = one_line.replace(char, ' ')       
        return one_line
    
    # Transfrom words to lower case 
    def transform_to_lower(self, one_line):
        return one_line.lower()
    
    # Lemmatize words assuming each word is a nound (pos = 'n')
    def lemmatize_words(self, one_line):
        wordnet_lemmatizer = WordNetLemmatizer()
        return wordnet_lemmatizer.lemmatize(one_line)
    
    # stemm words
    def stemming_words(self, one_line):
        # Algorithm Porter stemmer: Generate, Generically -> Gener, Gener
        # Algorithm Snowball stemmer: Generate, Generically -> Generat, Generic
        # Algorithm Lancaster stemmer: Generate, Generically -> Gen, Gen
        stemmer = PorterStemmer()
        #stemmer = SnowballStemmer("english")
        stemmed_line = [stemmer.stem(word) for word in one_line]
        return stemmed_line
         
#############################################################################################
# Extract Features 
#############################################################################################    
# https://sites.temple.edu/tudsc/2017/03/30/measuring-similarity-between-texts-in-python/  
# https://machinelearningmastery.com/prepare-text-data-machine-learning-scikit-learn/
    
    # turn text into vectors of term frequency (tf) without stemming 
    def wordCounts(self):
        # create an instance of the CountVectorizer class
        # Generate a new object from the class CountVectorizer() with the features
        # stop_words:
        #    english stop words, e.g. 'the', are removed 
        # min_df (opposite max_df):
        #    ignores terms that have a document frequency (presence in % of documents) strictly lower than the given threshold
        # max_features:
        #    limit the amount of features (vocabulary) that the vectorizer will learn
        vectorizer = CountVectorizer(stop_words='english', min_df=0.05)
        # call the fit() function in order to learn a vocabulary from one or more documents 
        vectorizer.fit(self.getCleanedInterests())
        print('The vocabulary of the researcher interests with the type {} is the following:\n'.format(type(vectorizer.vocabulary_)))
        self.vocabulary = vectorizer.vocabulary_
        
        index = 0
        words = [None] * len(self.vocabulary)
        counts = [None] * len(self.vocabulary)
        for key_ in self.vocabulary:
            print(key_, self.vocabulary[key_])
            words[index] = key_
            counts[index] = self.vocabulary[key_]
            index = index +1     
        
        y_pos = np.arange(len(words))
        plt.bar(y_pos, counts, align='center')
        plt.xticks(y_pos, words)
        plt.ylabel('Word Count')
        plt.title('Word Count of the Interests of the Researchers')
        plt.show()

        # call the transform() function on one or more documents as needed to encode each as a vector 
        vector = vectorizer.transform(self.getCleanedInterests())
        print('The shape of the word-count vector is {}'.format(vector.shape))
        print('The type of the vector is {}'.format(type(vector)))
        print('The array of the word count is the following: \n{}'.format(vector.toarray()))  
    
    # compute tf matrix with stemming     
    def stemTF(self):             
        StemVectorizer = CountVectorizer(tokenizer=self.StemNormalize, stop_words='english')
        StemVectorizer.fit_transform(self.getCleanedInterests())   
        
    def stemTfidf(self):
        stemTfidfVec = TfidfVectorizer(tokenizer=self.StemNormalize, stop_words='english')
        tfidf = stemTfidfVec.fit_transform(self.getCleanedInterests())
        return (tfidf * tfidf.T).toarray()    

    # calculate the Tfidf matrix of the interest words and print its features vocabulary, the idf matrix, the shape of the tfidf matrix and the the tfidf matrix itself
    def printTfidf(self):
        print('\nStart calculating Tfidf matrix...\n')
        # create an instance of the CountVectorizer class
        vectorizer = TfidfVectorizer()
        # call the fit() function in order to learn a vocabulary from one or more documents 
        vectorizer.fit(self.getCleanedInterests())
        print('The vocabulary of the interests is the following:\n{}'.format(vectorizer.vocabulary_))
        print('The idf matrix is the following:\n{}'.format(vectorizer.idf_))
        # call the transform() function on one or more documents as needed to encode each as a vector 
        vector = vectorizer.transform(self.getCleanedInterests())
        print('The shape of the transformed tfidf is the following:\n{}'.format(vector.shape))
        print('The transformed tfidf matrix is the following: \n{}'.format(vector.toarray()))    
    
    # the function StemTokens() stems each token of a given list of tokens and returns the result as a list 
    # input:
    # tokens:
    #    a list of tokens (words), which shall be stemmed
    # output:
    #    a list of the stemmed words 
    def StemTokens(self, tokens):
        stemmer = nltk.stem.porter.PorterStemmer()
        return[stemmer.stem(token) for token in tokens]
    
    # NLP words
    # 1. remove punctuation
    # 2. transform each word to lower case 
    # 3. stemm tokenized words 
    # input:
    # text:
    #    a list of raw words 
    # output:
    #    a list of normalized stemmed words
    def StemNormalize(self, text):
        remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
        return self.StemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))
    
    # compute the similarity among the interests of the researchers   
    def computeCosSimilarity(self):
        TfidfVec = TfidfVectorizer(tokenizer=self.StemNormalize, stop_words='english')
        tfidf = TfidfVec.fit_transform(raw_documents=self.getCleanedInterests())
        self.cosSim = (tfidf * tfidf.T).toarray()
        
    def printCosSim(self):
        if self.cosSim != []:
            num_col = len(self.cosSim)
            num_row = len(self.cosSim[0])
            print('The cosine similarity of the given interest words is shown in the following n_words x n_words matrix:\n Number of columns: {}, Number of rows: {}\n{}'.format(num_col, num_row, self.cosSim))
        else:
            print('You have to first execute the function computeCosSimilarity() before printing the cosine similarity matrix!\n Call [name_of_your_object].computeCosSimilarity()')
       
    # Build LSA Components to scale down data, not used yet in the analysis
    # Reference: http://www.datascienceassn.org/sites/default/files/users/user1/lsa_presentation_final.pdf
    def computeDTM(self):
        # Compute document-term matrix        
        dtm = self.vectorizer.fit_transform(self.getCleanedInterests())
        # each row represents a document, each column represents a word -> each document is a n-dim vector
        pd.DataFrame(dtm.toarray(), index=self.getCleanedInterests(), columns=self.vectorizer.get_feature_names())
        self.vectorizer.get_feature_names()
        
        return dtm
    
    def printDTM(self, dtm):
        dtm_df = pd.DataFrame(dtm.toarray(), index=self.getCleanedInterests(), columns=self.vectorizer.get_feature_names())
        print('The Document-term-matrix is the following: \n')
        print(dtm_df)
  
    def computeLSA(self, dtm):
        # Compute SVD and LSA
        dtm = dtm.asfptype()
        dtm_lsa = self.lsa.fit_transform(dtm)
        dtm_lsa = Normalizer(copy=False).fit_transform(dtm_lsa)
        
        return dtm_lsa
   
    def printLSAComponent(self):
        # Each LSA component is a linear combination of words 
        print('The components of the LSA are the following (rows: componentes; columns: words): \n')
        print(pd.DataFrame(self.lsa.components_, index= ['component_1', 'component_2'], columns=self.vectorizer.get_feature_names()))
        print('\n')

    def printLSADocuments(self, dtm_lsa):
        # Each document is a linear combination of the LSA components 
        print('The resulting ?? matrix from A = U*Sigma*V(transpose) is the following (rows: documents, columns: components):\n')
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
# Apply Standard Method Clustering 
#############################################################################################        
    # every clustering algorithm is using a distance metric, cosine similarity between words used as the distance matrix (normalization by document length) 
    def prepareClustMatrix(self):
        feature_distance = np.matrix(self.researcher_geo_data.loc[:,'distance'])
        #feature_isActive = np.matrix(self.researchers.loc[:,'isActive_int'])
        feature_cosSim = self.cosSim.transpose()
        feature_cosSim_single = np.matrix(feature_cosSim[:,[0]])
        self.X = np.append(feature_cosSim_single, np.reshape(feature_distance, (feature_cosSim.shape[0],1)), axis=1)
        self.X = np.append(self.cosSim, np.reshape(feature_distance, (self.cosSim.shape[0], 1)), axis = 1)
           
    # k-means clustering 
    # detect the right amount of clusters
    def elbowMethod(self, X):
        # k means determine k
        distortions = []
        K = range(1,50)
        for k in K:
            kmeanModel = KMeans(n_clusters=k).fit(X)
            kmeanModel.fit(X)
            distortions.append(sum(np.min(cdist(X, kmeanModel.cluster_centers_), axis=1)) / X.shape[0])
            
        # plot the elbow
        plt.plot(K,distortions, 'bx-')
        plt.xlabel('k')
        plt.ylabel('Distortion')
        plt.title('The Elbow Method showing the optimal k')
        plt.show()
    
    # apply k-means algorithm
    def computeKMeans(self, matrix, n):
        model = KMeans(n_clusters=n)
        model.fit(matrix)
        clust_labels = model.predict(matrix)         
        self.kmeans = pd.DataFrame(clust_labels)
        
    def computeDbscan(self):
        self.dbscanClust = DBSCAN(min_samples=1).fit_predict(self.cosSim)

    def plotClusterResults(self, clustLabels):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        scatter = ax.scatter(self.researcher_geo_data.loc[:,'distance'], # y-axe
                             self.researchers.loc[:,'isActive_int'], # x-axe
                             c = clustLabels[0],
                             s = 50)
        ax.set_title('Result of Clustering the Researcher Interests by their Similarity')
        ax.set_xlabel('Distance in Miles')
        ax.set_ylabel('Status of the Researcher (Former=0/ Current=1)')
        plt.colorbar(scatter)
        plt.show()
                       
#############################################################################################
# ManipulateGeo
#############################################################################################           
    #input: column 'origin' in a dataframe researchers_df
    #output: dataframe researcher_geo_df with the columns 'name', 'longtitude', 'latitude', 'country', 'city' -> necessary? -> yes, for clustering 
    #generate a new dataframe with the researcher's name as PK and additional columns named in the list/ array 'newHeader'
    def newResearcherTable(self):
        newDf = pd.DataFrame(self.researchers.loc[:,'id'])     
        newDf.loc[:,'address'] = pd.Series(index=newDf.index)
        newDf.loc[:,'longtitude'] = pd.Series(index=newDf.index)
        newDf.loc[:,'latitude'] = pd.Series(index=newDf.index)
        newDf.loc[:,'country'] = pd.Series(index=newDf.index)      
        return newDf
    
    def printResearcherGeoData(self, number):
        if number <= self.num_rows:
            print(self.researcher_geo_data.loc[0:number,:])
        else:
            print('The number of researchers in the dataframe is {}. The given number is >{}.'.format(self.num_rows,self.num_rows))

    # request geo data from OSM by location (column 'origin' with the name of the university)
    # Reference: https://operations.osmfoundation.org/policies/nominatim/
    # ToS - Requirements:
    #    No heavy uses (an absolute maximum of 1 request per second).
    #    Provide a valid HTTP Referer or User-Agent identifying the application (stock User-Agents as set by http libraries will not do).
    #    Clearly display attribution as suitable for your medium.
    #    Data is provided under the ODbL license which requires to share alike (although small extractions are likely to be covered by fair usage / fair dealing).
    def requestGeoDataOSM(self):
        print('Start looking up geo data from OSM. After each request the program pauses for 2 seconds to not violate the ToS of OSM.')
        origin_index = 0
        true_index = 0
        false_index = 0
        for origin in self.researchers.loc[:,'origin']:
            
            geolocator = Nominatim()
            researcher_geo_data = geolocator.geocode(origin)
            if researcher_geo_data: 
                self.researcher_geo_data.loc[origin_index, 'address'] = researcher_geo_data.address
                self.researcher_geo_data.loc[origin_index, 'longtitude'] = researcher_geo_data.longitude
                self.researcher_geo_data.loc[origin_index, 'latitude'] = researcher_geo_data.latitude                         
                true_index = true_index +1
            else:
                self.researcher_geo_data.loc[origin_index, 'address'] = 'Spandauer Str. 1, Berlin, Berlin, 10099, Germany'
                self.researcher_geo_data.loc[origin_index, 'longtitude'] = '52.5189879'
                self.researcher_geo_data.loc[origin_index, 'latitude'] = '-13.3925988' 
                self.researcher_geo_data.loc[origin_index, 'country'] = 'Germany'  
                false_index = false_index + 1            
            origin_index = origin_index +1
            time.sleep(2)
        
        # check lookup results 
        total = origin_index #len(researcher_geo_data.loc[:,'latitude'])    
        if (true_index + false_index) == total:
            print('All researchers have a location attached. \n Successfull lookups: {}/{}, Not successfull lookups: {}/{}'.format(true_index,total,false_index,total))
        else:
            print('Not all researchers have a location attached. \n Successfull lookups: {}/{}, Not successfull lookups: {}/{}'.format(true_index,total,false_index,total))
            
    # calculate the distance between one researcher and all others
    def calculateDistance(self, lat, long):
        self.researcher_geo_data.loc[:,'distance'] = pd.Series(index=self.researcher_geo_data.index)         
        researcher_fix = (lat, long)
               
        for researcher_index in range(0, self.num_rows):            
            researcher_A = (self.researcher_geo_data.loc[researcher_index,'latitude'],self.researcher_geo_data.loc[researcher_index,'longtitude'])
            self.researcher_geo_data.loc[researcher_index,'distance'] = distance.great_circle(researcher_A, researcher_fix).miles
   
    # Interactive map where each researcher is represented by one leaflet using the library geopy 
    # Reference: https://python-visualization.github.io/folium/quickstart.html      
    def visualizeGeoCode(self): 
        start_location = [52.5189879, -13.3925988]                    
        researcher_map = folium.Map(location=start_location, 
                         tiles = 'Stamen Terrain',  # built-in OpenStreetMap, Mapbox Bright, Mapbox Control Room, Stamen (Terrain, Toner, and Watercolor), Cloudmade and Mapbox only with API key
                         zoom_start=3, 
                         control_scale=True,
                         max_zoom = 15,
                         min_zoom = 1,
                         world_copy_jump = False)
        
        #http://python-visualization.github.io/folium/docs-v0.5.0/modules.html
        #labels_origin = self.researchers.loc[:,'origin'].values.tolist()
        #for researcher in self.researcher_geo_data.loc[:,'latitude']:
        for researcher_index in range(0, self.num_rows):
            # set marker features 
            long = float(self.researcher_geo_data.loc[researcher_index,'longtitude'])
            lat = float(self.researcher_geo_data.loc[researcher_index,'latitude'])
            html = 'Position: ' + self.researchers.loc[researcher_index,'position'] + '\n' #+ 'Origin: ' + self.researchers.loc[researcher_index,'origin']
            popup_researcher = folium.Popup(html=html, parse_html=True)    # popup takes as an input raw html-text
            #tooltip_researcher = self.researchers.loc[researcher_index,'id']    # only supported in the developer version
            color_researcher = self.color(self.researchers.loc[researcher_index,'isActive'])
            
            folium.Marker( 
                location = [lat,long],  # [latitude (NS), longitude (WE)]
                popup = popup_researcher,
                icon = folium.Icon(color=color_researcher, icon='info-sign')).add_to(researcher_map) 
                
        # export map to html-file to filename_geo
        filename_geo = self.path_irtg + 'researchers' + '_'+ 'geo' + '_' + str(self.timestamp) + '.html'
        print('Export data to {} .. \n'.format(filename_geo))               
        if researcher_map == []:
            raise ValueError('Map is empty')        
        try:
            researcher_map.save(filename_geo)
        except IOError as e:
            print('IOError', e.message)
           
    # define colour for marker on the researcher_map
    # input:
    #    parameter, which defines colour, e.g. isActive or Ranking of the scholar 
    # output:
    #    color depending on the input 
    def color(self, isActive):
        if isActive == True:
            col = 'green'
        else:
            col = 'orange'
        return col
                    

#############################################################################################
# Evaluate Results - sample tests
#############################################################################################     

    # naive benchmark: random groups 
    def chunks(self, shuffledResearchers, n):
        # yield successive n-sized chunks from list
        for i in range(0, len(shuffledResearchers), n):
            yield shuffledResearchers[i:i + n]
            
    def shuffle(self, researchers, numberClusters):
        #random.shuffle(researchers)
        return list(self.chunks(researchers, numberClusters))
    
    def printKMeans(self):
        print('The result of the K Means Clustering is the following (only first four clusters):\n')
        
        clust0 = []
        clust1 = []
        clust2 = []
        clust_others = []
        
        index_researcher = 0
        index_clust0 = 0
        index_clust1 = 0
        index_clust2 = 0
        index_clust_others = 0
        for label_index in range(0, len(self.kmeans)):    
            id_interest_tupel = (self.researchers.loc[index_researcher,'id'], self.researchers.loc[index_researcher,'cleanedInterests'])     
            if self.kmeans.loc[label_index,0] == 0:
                clust0.append(id_interest_tupel)
                index_clust0 +=1
            elif self.kmeans.loc[label_index,0] == 1:
                clust1.append(id_interest_tupel)
                index_clust1 +=1
            elif self.kmeans.loc[label_index,0] == 2:
                clust2.append(id_interest_tupel)
                index_clust2 +=1
            else:
                clust_others.append(id_interest_tupel)
                index_clust_others +=1
            
            index_researcher +=1
        
        print('Elements in Cluster 0: {}'.format(index_clust0)) 
        print('Cluster 0 has the following interests:\n')
        self.printArray(clustX=clust0)
        print('\n')
        
        print('Elements in Cluster 1: {}'.format(index_clust1))  
        print('Cluster 1 has the following interests:\n')
        self.printArray(clustX=clust1)
        print('\n')
        
        print('Elements in Cluster 2: {}'.format(index_clust1))
        print('Cluster 2 has the following interests:\n')
        self.printArray(clustX=clust2)
        print('\n')
          
        print('Elements in Cluster 4: {}'.format(index_clust_others)) 
        print('Cluster others has the following interests:\n')
        self.printArray(clustX=clust_others)
        print('\n')    
    
# AnalyseText.py    
