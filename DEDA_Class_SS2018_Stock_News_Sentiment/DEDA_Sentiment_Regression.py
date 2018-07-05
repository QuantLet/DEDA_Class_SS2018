# Import of packages used
from bs4 import BeautifulSoup
import re
import csv
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import quandl
import plotly.plotly as py
import plotly
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from PIL import Image
from wordcloud import WordCloud
import sys
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")

# Functions

def Words(filename = None, header = False, column = 0):
    sent_words = []
    if header == False:  
        try:
            with open(filename, errors = 'ignore') as f:
                        lm = csv.reader(f, delimiter=',')
                        for row in lm:
                            if column != 0:
                                if row[column] != '0':
                                    sent_words.append(row[0])
                            else:
                                sent_words.append(row[0])
        except:
            print('Error: Maybe wrong filename')
    else:
        try:
            with open(filename, errors = 'ignore') as f:
                        lm = csv.reader(f, delimiter=',')
                        for row in lm:
                            if column != 0:
                                if row[column] != '0':
                                    sent_words.append(row[0])
                            else:
                                sent_words.append(row[0])
            sent_words = sent_words[1:]
        except:
            print('Error: Maybe wrong filename')
        
    return(sent_words)


def plot_figures(figures, nrows = 1, ncols=1, name = 'Wordcloud.png'):
    fig, axeslist = plt.subplots(ncols=ncols, nrows=nrows)
    for ind,title in zip(range(len(figures)), figures):
        axeslist.ravel()[ind].imshow(figures[title], cmap=plt.gray())
        axeslist.ravel()[ind].set_title(title)
        axeslist.ravel()[ind].set_axis_off()
    plt.tight_layout()
    plt.figure(figsize=(10,10))
    fig.savefig(name, dpi = 720,transparent=True)

def Downloader(stock = None, symbol = None, quandl_api_key = 'Wf96zAVtLHhnKxuTUE_U'):

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
            tmp_stamp                = re.findall('"datePublished":".*?","',str(tmp_links[2]))[0].split('+')[0][17:].split('T')
            tmp_date                 = datetime.strptime(str(tmp_stamp[0]), '%Y-%m-%d').date()
            tmp_time                 = tmp_stamp[1]
            tmp_txt                  = re.findall('"articleBody":".*?;",',str(tmp_links[2]))[0][15:-3]
            if tmp_date in doc:
                doc[tmp_date]['Article'].append( (tmp_time,tmp_txt) ) 
            else:
                doc[tmp_date] = {'Article' : [(tmp_time,tmp_txt)]}
            print('Downloading article ',i,' out of ',len(article_links),' - Done')
            i += 1
        except:
            print('Downloading article ',i,' out of ',len(article_links)," - Not available")
            i += 1

    # start and end day of the articles
    start = datetime.strptime(str(min(doc.keys())), '%Y-%m-%d').date()
    end   = datetime.strptime(str(max(doc.keys())), '%Y-%m-%d').date()

    # extract historics quotes
    df = quandl.get("EOD/" + symbol, trim_start = start, trim_end = end, authtoken=quandl_api_key)

    # incorporate quotes into the articles dataframe
    pr_dates  = [datetime.strptime(str(date).split()[0],'%Y-%m-%d').date() for date in df.index.tolist()]
    pr_close  = [float(prize) for prize in df['Adj_Close']]
    pr_volume = [float(vol) for vol in df['Adj_Volume']]
    pr_logret = [0] + [np.log(df['Adj_Close'][i+1]) - np.log(df['Adj_Close'][i]) for i in range(len(df['Adj_Close'])-1)]
    pr_day_rg = [float(h) - float(l) for l,h in zip(df.Adj_Low,df.Adj_Close)]
    pr_on_rg  = [float(c) - float(o) for c,o in zip(df.Adj_Close,df.Adj_Open)]
    
    # extend doc with the qotes
    for element in list(zip(pr_dates,pr_close,pr_volume,pr_logret,pr_day_rg,pr_on_rg)):
        tmp_dict = {'Price' : element[1],
                    'Volume': element[2],
                    'Return': element[3],
                    'DayRG': element[4],
                    'OnRG' : element[5]}
        if element[0] in doc.keys():
            doc[element[0]].update(tmp_dict)
        else:
            doc[element[0]] = tmp_dict

    # create empty DataFrame and fill with nested dict values and keys
    ls = []

    for key in doc.keys():
        if 'Article' in doc[key]:
            for l in range(len(doc[key]['Article'])):
                if 'Price' in doc[key]:
                    ls.append([key,
                               doc[key]['Article'][l][0],
                               doc[key]['Article'][l][1],
                               doc[key]['Price'],
                               doc[key]['Return'],
                               doc[key]['Volume'],
                               doc[key]['DayRG'],
                               doc[key]['OnRG']])
                else:
                    ls.append([key,
                               doc[key]['Article'][l][0],
                               doc[key]['Article'][l][1],
                               np.nan,
                               np.nan,
                               0,
                               0,
                               0])
        else:
            if 'Price' in doc[key]:
                ls.append([key,
                           np.nan,
                           np.nan,
                           doc[key]['Price'],
                           doc[key]['Return'],
                           doc[key]['Volume'],
                           doc[key]['DayRG'],
                           doc[key]['OnRG']])
            else:
                ls.append([key,
                           np.nan,
                           np.nan,
                           np.nan,
                           np.nan,
                           0,
                           0,
                           0])

    df         = pd.DataFrame.from_records(ls)
    df.columns = ['Date', 'Time', 'Text', 'Price','Return','Volume', 'DayRG','OnRG']
    
    return([df,article_links])


def shifter(dates = None, dataset = None, column = None, FUN = np.mean, tops = False):
    
    var = []
    for date in dates:
        if len(column.loc[dataset['Date'] == date ]) > 1:
            if tops == False:
                var.append(float(FUN(column.loc[dataset['Date'] == date ])))
            else:
                var.append(float(column.loc[dataset['Date'] == date].head(1))) 
        else:
            var.append(float(column.loc[dataset['Date'] == date ]))
    var = [0] + var
    
    return(var)

def RegressionTrainer(data = None, split = 0.8, model = None, alpha = [0,0.05,0.1,0.15,0.2,0.25,0.3], intercept = True):
    
    Dates_train                      = data['Date'].head(int(len(data)*split))
    Dates_test                       = data['Date'].tail(int(len(data)*(1 - split)))
    X                                = data.drop(['Date','y'],1)
    Y                                = data['y']
    
    # For Training and Testing
    X_train = np.array(X.head(int(len(X)*split)))
    X_test  = np.array(X.tail(int(len(X)*(1 - split))))
    Y_train = np.array(Y.head(int(len(Y)*split)))
    Y_test  = np.array(Y.tail(int(len(Y)*(1 - split))))
    
    # For returnin in results
    Train_X = pd.concat( [ Dates_train, X.head(int(len(X)*split))], axis = 1)
    Test_X  = pd.concat( [ Dates_test , X.tail(int(len(X)*(1 - split)))], axis = 1)
    Train_Y = pd.concat( [ Dates_train, Y.head(int(len(Y)*split))], axis = 1)
    Test_Y  = pd.concat( [ Dates_test , Y.tail(int(len(Y)*(1 - split)))], axis = 1)
    
    res_data = [Train_X, Test_X, Train_Y, Test_Y]
    
    Const    = 0 
    
    if model == 'LR':
        if intercept == True:
            Const                            = 1
            X_train                          = sm.add_constant(X_train)
            X_test                           = sm.add_constant(X_test)
            
            for d in res_data:
                d['Const'] = 1
        
        LR                                = sm.OLS(Y_train, X_train)
        LR_est                            = LR.fit()
        LR_est_pred                       = LR_est.predict(X_test)
        LR_RMSD                           = np.sqrt(np.mean((LR_est_pred - Y_test)**2))

        print(LR.fit().summary())
        print('Root Mean Square Deviation:' + str(LR_RMSD))
    
        results                           = [LR_est,Train_X, Test_X, Train_Y, Test_Y, Const]
        
    elif model == 'Lasso':
        if intercept == True:
            Const                            = 1
            X_train                          = sm.add_constant(X_train)
            X_test                           = sm.add_constant(X_test)
        
            for d in res_data:
                d['Const'] = 1

        Lasso                                = sm.OLS(Y_train, X_train)
        l                                    = []
        
        for a in alpha:
            Lasso_est                        = Lasso.fit_regularized(L1_wt = 1, alpha = a)
            Lasso_est_pred                   = Lasso_est.predict(X_test)
            Lasso_RMSD                       = np.sqrt(np.mean((Lasso_est_pred - Y_test)**2))
            l.append((a,Lasso_RMSD))
            
        a_min                            = min(l, key = lambda t: t[1])[0]
        Lasso_est                        = Lasso.fit_regularized(L1_wt = 1, alpha = a_min)
        Lasso_est_pred                   = Lasso_est.predict(X_test)
        Lasso_RMSD                       = np.sqrt(np.mean((Lasso_est_pred - Y_test)**2))
            
        print('Root Mean Square Deviation:' + str(Lasso_RMSD))

        results = [Lasso_est, a_min, split, Train_X, Test_X, Train_Y, Test_Y, l, Const]
    
    return(results)

def DataValueGetter(df = None, data = None, col_df = None, col_raw = None, mean_return = 0, Scaling = False):
    d = datetime.strptime(str('2000-01-01'), '%Y-%m-%d').date()
    l = 0
    if datetime.now().date() in df.index:
        l       = [df[col_df].loc[datetime.now().date()]]
        d       = datetime.now().date()
        result  = [l,d]
    else:
        i = 1
        while list(data[col_raw][data.Date == datetime.now().date() - timedelta(days=i - 1)].unique()) == []:
            i += 1
        l = data[col_raw][data.Date == datetime.now().date() - timedelta(days=i - 1)].unique()
        d = datetime.now().date() - timedelta(days=i - 1)
        result  = [l,d]
    if Scaling == True:    
        if datetime.now().date() == d:
            result = [l,d]
        else:
            days    = (datetime.now().date()  - d).days
            result  = [l * np.exp(days * mean_return),d]
    return(result)

def RealTimeForecaster(stock = None, 
                       symbol = None, 
                       model = None, 
                       Const = 0, 
                       agg_data = None , 
                       quandl_api_key = 'Wf96zAVtLHhnKxuTUE_U', 
                       past_articles = None):



    article_links = []
    tmp_links     = []

    # Check for new articles
    base          = 'https://www.finanzen.net'
    html          = requests.get(base + '/news/' + stock + '-News@intpagenr_1')
    soup          = BeautifulSoup(html.text, "html5lib")

    # Search all news article links on the website
    links         = soup.select('.news-list td')

    # Extract all article links
    tmp_links     = [str(re.findall('href="/nachricht/aktien/.*?"', str(link))[0])[6:-1] for link in links 
                     if re.findall('href="/nachricht/aktien/.*?"', str(link))]

    if tmp_links  != []:
        for link in tmp_links:
            if link not in past_articles:
                print('New Article Link')
                article_links.append(link)
    
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
                tmp_stamp                = re.findall('"datePublished":".*?","',str(tmp_links[2]))[0].split('+')[0][17:].split('T')
                tmp_date                 = datetime.strptime(str(tmp_stamp[0]), '%Y-%m-%d').date()
                tmp_time                 = tmp_stamp[1]
                tmp_txt                  = re.findall('"articleBody":".*?;",',str(tmp_links[2]))[0][15:-3]
                if tmp_date in doc:
                    doc[tmp_date]['Article'].append( (tmp_time,tmp_txt) ) 
                else:
                    doc[tmp_date] = {'Article' : [(tmp_time,tmp_txt)]}
                print('Downloading new article ',i,' out of ',len(article_links),' - Done')
                i += 1
            except:
                print('Downloading new article ',i,' out of ',len(article_links)," - Not available")
                i += 1

    # start and end day of the new articles incl some old days
    start = datetime.strptime(str(min(doc.keys())), '%Y-%m-%d').date()      
    end   = datetime.now().date()            

    # extract historics quotes
    df    = quandl.get("EOD/" + symbol, trim_start = start, trim_end = end, authtoken=quandl_api_key)
    
    pr_close  = DataValueGetter(df = df, data = agg_data, col_df = 'Adj_Close', col_raw = 'y', mean_return = np.mean(agg_data.Return))[0][0]
    pr_dates  = datetime.now().date()
    pr_volume = DataValueGetter(df = df, data = agg_data, col_df = 'Adj_Volume', col_raw = 'Volume', mean_return = np.mean(agg_data.Return), Scaling = False)[0][0]
    pr_logret = np.mean(agg_data.Return)
    pr_day_rg = np.mean(agg_data.DayRG)
    pr_on_rg  = np.mean(agg_data.OnRG)
    
    element = [pr_dates,pr_close,pr_volume,pr_logret,pr_day_rg,pr_on_rg]
    tmp_dict = {'Price' : element[1],
                'Volume': element[2],
                'Return': element[3],
                'DayRG': element[4],
                'OnRG' : element[5]}
    if element[0] in doc.keys():
        doc[element[0]].update(tmp_dict)
    else:
        doc[element[0]] = tmp_dict

    # create empty DataFrame and fill with nested dict values and keys
    ls = []

    for key in doc.keys():
        if 'Article' in doc[key]:
            for l in range(len(doc[key]['Article'])):
                if 'Price' in doc[key]:
                    ls.append([key,
                               doc[key]['Article'][l][0],
                               doc[key]['Article'][l][1],
                               doc[key]['Price'],
                               doc[key]['Return'],
                               doc[key]['Volume'],
                               doc[key]['DayRG'],
                               doc[key]['OnRG']])
                else:
                    ls.append([key,
                               doc[key]['Article'][l][0],
                               doc[key]['Article'][l][1],
                               np.nan,
                               np.nan,
                               0,
                               0,
                               0])
        else:
            if 'Price' in doc[key]:
                ls.append([key,
                           np.nan,
                           np.nan,
                           doc[key]['Price'],
                           doc[key]['Return'],
                           doc[key]['Volume'],
                           doc[key]['DayRG'],
                           doc[key]['OnRG']])
            else:
                ls.append([key,
                           np.nan,
                           np.nan,
                           np.nan,
                           np.nan,
                           0,
                           0,
                           0])

    df         = pd.DataFrame.from_records(ls)
    df.columns = ['Date', 'Time', 'Text', 'Price','Return','Volume', 'DayRG','OnRG']
    
    # Incorporate Score Columns
    df = pd.concat([df, pd.DataFrame(columns = ['PosScore']),
                      pd.DataFrame(columns = ['NegScore']),
                      pd.DataFrame(columns = ['TotalWordCount']),
                      pd.DataFrame(columns = ['SentScore'])])

    bow_neg = []
    bow_pos = []

    # remove Links and Special Characters
    for i,article in enumerate(df.Text):
        if str(article) != 'nan':
            # Get rid of punctuation
            tmp_word_list    = ' '.join(' '.join(article.split(',')).split('.')).split()
            # Get rid of special characters
            df.Text[i]       = ' '.join([ word for word in tmp_word_list if word.isalnum() ])   
            # Get rid of stopwords
            df.Text[i]       = ' '.join([w for w in df.Text[i].split() if not w.upper() in stopwords])
            # Calculate positive & negative words per article and assign them to DataFrame
            p,n = 0,0
            for word in article.split(' '):
                   if word.upper() in pos:
                        p += 1
                        bow_pos.append(word)
                   if word.upper() in neg:
                        n += 1
                        bow_neg.append(word)
            df.PosScore[i]       = p
            df.NegScore[i]       = n
            df.TotalWordCount[i] = len(article.split(' '))
            if p == 0 and n == 0:
                df.SentScore[i]  = 0
            else:
                df.SentScore[i]  = (p-n)/(p+n)

    df = df.sort_values(['Date','Time']) 
    
    df_agg            = pd.DataFrame(columns = ['SentScore','Return','Volume', 'DayRG', 'OnRG', 'NoW', 'PrevP'])

    df_agg.PrevP     = [df.sort_values(by = 'Date',ascending = False).Price.unique()[0]]
    df_agg.Return    = [df.sort_values(by = 'Date',ascending = False).Return.unique()[0]]
    df1              = df.sort_values(by = 'Date',ascending = False).fillna(method = 'pad')
    df1              = df1.sort_values(by = 'Date',ascending = False).fillna(method = 'bfill')
    if not df1.SentScore[df1.SentScore != 0].empty:
        df_agg.SentScore = [np.mean(df.SentScore[df.SentScore != 0])]
    else:
        df_agg.SentScore = [0]
    df_agg.Volume    = [df.sort_values(by = 'Date',ascending = False).Volume.unique()[0]]
    df_agg.OnRG      = [df.sort_values(by = 'Date',ascending = False).OnRG.unique()[0]]
    df_agg.DayRG     = [df.sort_values(by = 'Date',ascending = False).DayRG.unique()[0]]
    df_agg.NoW       = [np.sum(df.TotalWordCount)]

    if Const == 1:
        df_agg['Const']  = 1
        cols             = list(df_agg.columns.values)
        cols             = ['Const'] + cols[:-1]
        df_agg           = df_agg[cols]
    
    return([df,df_agg, model[0].predict(df_agg) ])

def Plotter(forecast = False, data1 = None , model = None, prediction = None ):
    data1  = data1.sort_values(by=['Date'])
    data1  = data1.fillna(method='pad')
    cols   = list(model[2].columns.values)
    cols   = ['Const'] + cols[:-1]


    g = data1.sort_values(by=['Date']).groupby('Date').Price
    t = data1.sort_values(by=['Date'])[data1.Text.isnull() == False].groupby('Date').Price

    # Plotting
    plotly.tools.set_credentials_file(username='gauermar', api_key='f1Cwgh68yBTu868slqky')

    # Create List of lists with texts
    texts = []

    for date in data1.sort_values(by=['Date']).Date[data1.Text.isnull() == False].unique():
        texts.append([text for text in data1.Text[data1.Date == date]][0])



    Quotes = go.Scatter(
        x = data1.sort_values(by=['Date']).Date.unique(),
        y = [float(p) for p in pd.concat([g.unique()], axis=1, keys=['Price']).Price],
        mode = 'lines',
        text = 'Stock Price',
        name = 'Stock Price'
    )

    Articles = go.Scatter (
        x = data1.sort_values(by=['Date']).Date[data1.Text.isnull() == False].unique(),
        y = [float(p) for p in pd.concat([t.unique()], axis=1, keys=['Price']).Price],
        text = ['No. of Articles: ' + str(p) for p in data1[data1.Text.isnull() == False].groupby('Date').agg('count').Text],#raw_data.Text != np.nan
        mode = 'markers',
        name = 'Articles'
        )
    
    TestForecast = go.Scatter (
            x = model[2].Date,
            y = model[0].predict(model[2][cols].drop('Date',1)),
            text = '1-Day Test Forecasts',
            mode = 'markers',
            name = '1-Day Test Forecasts'
            )
    if forecast == False:
        data = [Quotes, Articles, TestForecast]
        
    else:
        
        Forecast = go.Scatter (
            x    = datetime.now().date() + timedelta(days=1),
            y    = float(df[2][0]),
            text = '1-Day Forecast',
            mode = 'markers',
            name = '1-Day Forecast'
            )

        data = [Quotes, Articles, TestForecast, Forecast]
        
        
    layout = go.Layout(
        showlegend=True,
        legend=dict(orientation="h"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
        showgrid=False
        ),
        yaxis=dict(
            showgrid=False,
        )
    )
    fig = go.Figure(data=data, layout=layout)
    return(fig)

# Main

# Data Preperation
stock         = 'Travelers' # Please type in the name as described in the presentation (corresponding to the link structure of finanzen.net)
symbol        = 'TRV'  # Symbol in terms of the Quandl-EOD dataset

# Load the LM-Wordlists in English and German
eng_neg_words = Words(filename = 'LM_Dict.csv',header = True, column = 7)
eng_pos_words = Words(filename = 'LM_Dict.csv',header = True, column = 8)

de_neg_words  = Words(filename = 'BPW_Neg.csv',header = False, column = 0)
de_pos_words  = Words(filename = 'BPW_Pos.csv',header = False, column = 0)

neg           = eng_neg_words + [w.upper() for w in de_neg_words]
pos           = eng_pos_words + [w.upper() for w in de_pos_words]

# Download articles
down     = Downloader(stock = stock, symbol = symbol)
raw_data = down[0]
data     = raw_data

# Incorporate Score Columns
data = pd.concat([data, pd.DataFrame(columns = ['PosScore']),
                  pd.DataFrame(columns = ['NegScore']),
                  pd.DataFrame(columns = ['TotalWordCount']),
                  pd.DataFrame(columns = ['SentScore'])])


# incorporate stopwords
de_stopwords = [w.upper() for w in Words('de_stopwords.csv')]
en_stopwords = Words('en_stopwords.csv')
stopwords    = de_stopwords + en_stopwords + ['WEITER', 'ZUM', 'ARTIKEL', 'BEI']

# Define Mask for stopwords
mask = np.array(Image.open('mask-cloud.png'))

bow_neg = []
bow_pos = []

# remove Links and Special Characters
for i,article in enumerate(data.Text):
    if str(article) != 'nan':
        # Get rid of punctuation
        tmp_word_list    = ' '.join(' '.join(article.split(',')).split('.')).split()
        # Get rid of special characters
        data.Text[i]       = ' '.join([ word for word in tmp_word_list if word.isalnum() ])   
        # Get rid of stopwords
        data.Text[i]       = ' '.join([w for w in data.Text[i].split() if not w.upper() in stopwords])
        # Calculate positive & negative words per article and assign them to DataFrame
        p,n = 0,0
        for word in article.split(' '):
               if word.upper() in pos:
                    p += 1
                    bow_pos.append(word)
               if word.upper() in neg:
                    n += 1
                    bow_neg.append(word)
        data.PosScore[i]       = p
        data.NegScore[i]       = n
        data.TotalWordCount[i] = len(article.split(' '))
        if p == 0 and n == 0:
            data.SentScore[i]  = 0
        else:
            data.SentScore[i]  = (p-n)/(p+n)

data = data.sort_values(['Date','Time']) 

# Create WordCloud for pos and neg words
wc_neg = WordCloud(background_color="rgba(0, 0, 0, 0)", mode="RGBA", max_words=2000, mask=mask)
fig_neg = wc_neg.generate(' '.join(bow_neg))
wc_pos = WordCloud(background_color="rgba(0, 0, 0, 0)", mode="RGBA", max_words=2000, mask=mask)
fig_pos = wc_pos.generate(' '.join(bow_pos))
wc_com = WordCloud(background_color="rgba(0, 0, 0, 0)", mode="RGBA", max_words=2000, mask=mask)
fig_com = wc_com.generate(' '.join(bow_pos + bow_neg))

fig = {'Negative WC': fig_neg,
       'Positive WC': fig_pos,
       'Combined WC': fig_com}
    
plot_figures(fig, 1, 3)

print('-----------------------------------> Preparing Data for Forecasting')
ml_data           = pd.DataFrame(columns = ['Date','y','SentScore','Return','Volume', 'DayRG', 'OnRG', 'NoW', 'PrevP'])
ml_data.Date      = sorted(list(set([datetime.strptime(str(date), "%Y-%m-%d").date() for date in data.Date.unique()])))

nearest_dates     = []

for i in range(len(ml_data.Date[1:])):
    nearest_dates.append(max([date for date in ml_data.Date if date < datetime.strptime(str(ml_data.Date[i+1]), '%Y-%m-%d').date()]))


y                  = shifter(ml_data.Date,data,data.Price,tops = True)[1:]
SentScore          = shifter(nearest_dates,data,data.SentScore)
NoW                = shifter(nearest_dates,data,data.TotalWordCount,sum)
Return             = shifter(nearest_dates,data,data.Return,tops = True)
prev_price         = shifter(nearest_dates,data,data.Price,tops = True)
Volume             = shifter(nearest_dates,data,data.Volume,tops = True)
on_rg              = shifter(nearest_dates,data,data.OnRG,tops = True)
day_rg             = shifter(nearest_dates,data,data.DayRG,tops = True)

ml_data.y         = y
ml_data.PrevP     = prev_price
ml_data.Return    = [np.nanmean(Return) if np.isnan(x) else x for x in Return]
ml_data.SentScore = list(np.nan_to_num(SentScore))
ml_data.Volume    = Volume
ml_data.OnRG      = on_rg
ml_data.DayRG     = day_rg
ml_data.NoW       = list(np.nan_to_num(NoW))

ml_data           = ml_data.loc[ml_data['Date'] != datetime.strptime(str(min(ml_data.Date)), "%Y-%m-%d").date()]
ml_data           = ml_data.fillna(method='pad')
ml_data           = ml_data.fillna(method='bfill')

print('-----------------------------------> Training the Models')
LR    = RegressionTrainer(data = ml_data, split = 0.8, model = 'LR', intercept = True)

# Graphics
df = []
while df == []:
    try:
        df = RealTimeForecaster(stock = stock, symbol = symbol, model = LR, Const = 1, agg_data = ml_data , quandl_api_key = 'Wf96zAVtLHhnKxuTUE_U', past_articles = down[1])
    except:
        print(datetime.now().time().strftime('%H:%M:%S -> ') + 'No New Articles. Retry in 5 min')
        time.sleep(5*60)
        continue
    print('Current Forecast for tomorrow: ' + str(float(df[2][0])))

pic_raw = Plotter(data1 = raw_data, model = LR, forecast = True, prediction = float(df[2][0]))

# Link for the graphic
print('Please Note: See the link for the Plotly-plot')
print(py.iplot(pic_raw).resource)
