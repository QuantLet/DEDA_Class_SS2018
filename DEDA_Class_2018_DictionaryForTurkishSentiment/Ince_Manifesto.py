#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 11:01:39 2018

@author: cemre
"""

import pandas as ps

from bs4 import BeautifulSoup

import requests

import string
from nltk.corpus import stopwords

import matplotlib.pyplot as plt

from wordcloud import WordCloud

from PIL import Image 

from googletrans import Translator

translator = Translator()


url = "https://www.muharremince.com.tr/tr/gelecek-bildirgesi"

incemanif = requests.get(url)  
html = incemanif.text  
manifsoup = BeautifulSoup(html, 'html.parser')
print(manifsoup.find('main', {"id" : "main"}).text)

maniftext = str(manifsoup.find('main', {"id" : "main"}).text)
#Removing the punctuation and making the words lowercase
translator = str.maketrans('', '', string.punctuation)
#print(text.translate(translator))

maniftext = maniftext.translate(translator).lower()

# Creating a dictionary for the words in the text

dat = list(maniftext.split())
dict1 = {}
for i in range(len(dat)):
    word = dat[i]
    dict1[word] = dat.count(word)
 
#Checking the listed stopwords in NLTK package
#stop_words = stopwords.words('turkish')

#Importing the extended stopwords list
#Resource: https://github.com/ahmetax/trstop/blob/master/dosyalar/derlemtr2016-10000.txt
stoplist = open("swNI.csv", "r")
stopwords = stoplist.readlines()
stopwords = [i.replace('"', '') for i in stopwords]
stopwords = [i.replace('\n', '') for i in stopwords]

#print(stopwords)

#Removing stopwords
keys = list(dict1)
keys = [i.replace('"', '') for i in keys]
keys = [i.replace("'", '') for i in keys]
filtered_words = [word for word in keys if word not in stopwords]
#filtered_words = [i.replace('i̇', 'i') for i in filtered_words]
dict2 = dict((k, dict1[k]) for k in filtered_words if k in filtered_words)


def SequenceSelection(dictionary, length, startindex = 0): 
    
    lengthDict = len(dictionary)
    if length > lengthDict:
        return print("length is longer than dictionary length");
    else:
        d = dictionary
        items = [(v, k) for k, v in d.items()]
        items.sort()
        items.reverse()   
        itemsOut = [(k, v) for v, k in items]
    
        highest = itemsOut[startindex:startindex + length]
        dd = dict(highest)
        wanted_keys = dd.keys()
        dictshow = dict((k, d[k]) for k in wanted_keys if k in d)

        return dictshow;
    
dictshow = SequenceSelection(dictionary = dict2, length = 7, startindex = 0)

# Visualizing the frequent words in Turkish

n = range(len(dictshow))
plt.bar(n, dictshow.values(), align='center')
plt.xticks(n, dictshow.keys(), rotation = 45)
plt.title("Ince Manif Most Frequent Words")
plt.savefig("Ince Manif FrequentWords.png", transparent=True, dpi=1000)

#Translating most frequest words into English
from googletrans import Translator

translator = Translator()


eng_FQwords = []

for fqword in list(dictshow):
    trs = translator.translate(fqword, src = 'tr', dest = 'en')
    eng_FQwords.append(trs.text)
    
print(eng_FQwords)

# Visualising the most frequent words in English
n = range(len(eng_FQwords))
plt.bar(n, dictshow.values(), align='center')
plt.xticks(n, eng_FQwords, rotation = 45)
plt.title("Ince Election Manifesto - Most Frequent Words")
plt.tight_layout()  
plt.savefig("Ince Menif FrequentWordsEN.png", transparent=True, dpi=1000)


# Creating the word cloud of filtered words in Turkish
###### Face of erdogan as a mask IN PROGRESS ######
import numpy as np
from os import path
import os
root_path = os.getcwd()


map_mask = np.array(Image.open(path.join(root_path, "trmap.png")))


filtered_WC = ' '.join(filtered_words)
filtered_WC = filtered_WC.replace('i̇', 'i')
filtered_WC = filtered_WC.replace('"', '')
filtered_WC = filtered_WC.replace("'", '')
wordcloud_FW = WordCloud(background_color='white', mask=map_mask, mode='RGBA').generate(filtered_WC)

plt.figure()
plt.imshow(wordcloud_FW, interpolation='bilinear')
plt.axis("off")
plt.imshow(map_mask, cmap=plt.cm.gray, interpolation='bilinear', alpha =0.2)
#plt.axis("off")
plt.title("Ince Manifesto Word Cloud")
plt.savefig("Ince Manifesto Word CloudTR.png", transparent=True, dpi=1000)
plt.show()


# Creating the word cloud of filtered words in english
from googletrans import Translator

translator = Translator()

eng_fil_words = []

for filword in filtered_words:
    trs = translator.translate(filword, src = 'tr', dest = 'en')
    eng_fil_words.append(trs.text)
#    print(eng_fil_words)
 #   eng_fil_words

filtered_WC_eng = ' '.join(eng_fil_words)
#filtered_WC_eng = filtered_WC.replace('i̇', 'i')
filtered_WC_eng = filtered_WC_eng.replace('"', '')
filtered_WC_eng = filtered_WC_eng.replace("'", '')
wordcloud_FW_eng = WordCloud(background_color='white', mask=map_mask, mode='RGBA').generate(filtered_WC_eng)

plt.figure()
plt.imshow(wordcloud_FW_eng, interpolation='bilinear')
plt.axis("off")
plt.imshow(map_mask, cmap=plt.cm.gray, interpolation='bilinear', alpha=0.2)
plt.title("Ince Election Manifesto - Word Cloud")
plt.savefig("Ince Election Manifesto - Word CloudEN.png", transparent = True,  dpi=1000)
plt.show()

