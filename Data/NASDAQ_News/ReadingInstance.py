import json

path = 'your working directory path'

with open(path + 'NASDAQ_News_2016.json', 'r') as json_file:
    nasdaq_news_2017 = json.load(json_file)

