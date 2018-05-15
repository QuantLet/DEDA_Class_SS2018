#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 12 12:42:41 2018

@author: Natalie
"""

import requests
from bs4 import BeautifulSoup

def download(url, num_retries=2, proxies=None):
    print('Downloading: ', url)
    try:
        # resp = requests.get(url, headers=headers, proxies=proxies, timeout=5)
        resp = requests.get(url, proxies=proxies, timeout=5)
        html = resp.text
        if resp.status_code >= 400:
            print('Download error: ', resp.text)
            html = None
        if num_retries and 500 <= resp.status_code < 600:
            return download(url, num_retries -1)
    except requests.exceptions.RequestException as e:
        print('Download error: ', e.reason)
        html = None
    return html



print('--- Start of Program ---')

# Download url
former_irtg_url = 'https://www.wiwi.hu-berlin.de/de/forschung/irtg/guests/former-guests'
my_headers = {
        'name': 'natalie.habib@student.hu-berlin.de',
        'user agent': ''
        }
retries = 2

former_irtg_html = download(former_irtg_url, retries)
soup = BeautifulSoup(former_irtg_html, 'lxml')
#print(soup.text)


print('--- End of Program ---')

#setup.py
