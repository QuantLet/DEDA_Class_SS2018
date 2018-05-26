'''
Created on May 12, 2018

@author: Natalie

credits:
    https://hackernoon.com/web-scraping-tutorial-with-python-tips-and-tricks-db070e70e071
    https://books.google.de/books?id=jHc5DwAAQBAJ&printsec=frontcover&dq=What+is+data+scraping&hl=de&sa=X&ved=0ahUKEwi2-6aa1IDbAhWR16QKHUdzC6YQ6AEIKDAA#v=onepage&q&f=false

'''

from HTMLTableParser import HTMLTableParser 
import pandas as pd

print('--- Start of Program --- \n')

irtg_url = 'https://www.wiwi.hu-berlin.de/de/forschung/irtg/guests/former-guests'
my_headers = {
        'name': 'natalie.habib@student.hu-berlin.de',
        'user agent': ''
        }
retries = 2

hp = HTMLTableParser()
table = hp.download(irtg_url, retries)
print(table)

table = pd.DataFrame(table)
table.to_csv('former_irtg.csv')

print('--- End of Program ---')

# main.py
