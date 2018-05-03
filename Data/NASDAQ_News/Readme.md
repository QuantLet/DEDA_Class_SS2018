# NASDAQ News Database 2016

NASDAQ News data is collected from NASDAQ News platform (https://www.nasdaq.com) that offers news related to Global Market, US Stock Market, US Fix-income Market and etc.
This dataset can only be used on academic research purpose.

# Download Link:

https://drive.google.com/open?id=1YU6WgUffJj73q23tMB1ipUUzTzXSI6RJ


## Format: 

Json format, reading example in Python is provided as following:

Note: Please unzip the json.zip file before reading it

```python
import json

path = 'your working directory path'

with open(path + 'NASDAQ_News_2016.json', 'r') as json_file:
    nasdaq_news_2016 = json.load(json_file)
```

## Time range: 

2016.01.01-2016.12.31, one year sample, 162144 articles in total.

## Features:

article_link: The original link for the article

article_title: The title of the article

article_time: The posted time of the article, string format, UTC -5 time (New York Time)

author_name: Name of the author(s)

author_link: Link to the author(s)'s homepage

article_content: Main body content of the article

appears_in: Tags for article's, e.g Investing, Stocks, Options and so on

symbols: Tickers that are related to the article


## Person to contact regarding the dataset

hujunjie@hu-berlin.de

