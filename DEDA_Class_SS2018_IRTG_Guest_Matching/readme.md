Readme
Profile Matching in Academic Networks – The approach to form new groups of researchers by their digital profile, especially their research interests, require that a computer program retrieves information from websites and applies clustering and classification methods as well as similarity measurements on the retrieved data. Three challenges exist. Firstly, to target a number of profiles from the same research fields, secondly, the small number of words, in which scholars describe their research interest and thirdly, the selection of the clustering and classification method.
In the following python-project, profiles of former and current scholars from the International Research Traning Group (IRTG) 1792 working in the field of high-dimensional non-stationary time series build the data basis which limits the common research field. After pre-processing and represent the text to computers, the author applies the cluster method k-means. 
Structure and Content of the python-project folder (working project)
The project folder contains the two folders ‘web scraping’ and ‘TextAnalytics’. The first folder implements the functionality to download, parse and save the content from the target-websites in a CSV-file. The second folder provides function to clean, pre-process and analyze the interests of the scholars and visualize their geo data on a world map. The following list shows the functions: 

WebScraping.scrape.py
-    __init__
-    setHomePath
-    download
-    getDataFrame
-    HTML2df
-    ParseHTMLTable
-    getContent
-    writeCSV
-    concatCurrentFormerDf

TextAnalytics.AnalyseText.py
-    __init__
-    readCSV
-    getFilePath
-    getCleanedInterests
-    __str__
-    splitName
-    pre_process
-    filtering_stop_words
-    filtering_punctuation
-    transform_to_lower
-    lemmatize_words
-    computeDTM
-    computeLSA
-    printLSAComponent
-    printLSADocuments
-    printDocumentSimilarity
-    Improve: clusterComponents
-    ToDo: classifyComponentsDt
-    newResearcherTable
-    requestGeoData
-    ToDo: calculateDistance 
-    ToDo: visualizeGeoDistribution
To run the project-folder make sure that all neccesary python libraries are installed. The project folder was implemented in Eclipse Oxygen on a Windows 8 OS.
ToDo: Test in Anaconda on an iOS