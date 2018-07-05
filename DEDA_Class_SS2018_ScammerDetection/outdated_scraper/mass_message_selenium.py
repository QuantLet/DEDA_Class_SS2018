#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 21 12:55:58 2018

@author: jessiehsieh
"""

import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select

from random import randint

project_directory 	    = '/Users/jessiehsieh/Documents/Programming/Data_Science/WebScraping/Scrap_search_page/'
csv_file_name_fullinfo 	= project_directory + 'wggesucht_angebote_full.csv'
offers_to_send_request  = pd.read_csv(csv_file_name_fullinfo)

offers_to_send = len(offers_to_send_request[offers_to_send_request.request_sent < 1])
print('%d messages is yet to be sent.' % (offers_to_send))

# example exception
option = webdriver.ChromeOptions()
#option.add_argument("--incognite")

# create new instance of chrome in incognite mode
browser = webdriver.Chrome(executable_path = '/Users/jessiehsieh/Documents/Programming/Data_Science/WebScraping/DPD/chromedriver', chrome_options = option)

application = 'Hi, my name is Sally. Sorry for not using German because I am still learning! :) \n I have read your room offer and I am very interested to rent it for my study of German language next month! I am a clean and tidy girl, so I will be a good flatmate! \n Hope to hear from you soon!'

message_sent = 0

for index, row in offers_to_send_request.iterrows():

    nap = 60 + randint(0, 9)

    if (row['request_sent'] == 0):
    		
        # take a nap first
        print('initializing the offer page in %d sec...' % (nap))
        time.sleep(nap)
        # go to website of interest
   		#    browser.get("http://www.dpd.co.uk/apps/tracking/?reference=4454155341#results")
        browser.get('https://www.wg-gesucht.de/' + row['link'])
        # wait up to 20 seconds for the page to load
        timeout = 60
        try:
            # the core to click and send message
            page_show = WebDriverWait(browser, timeout).until((EC.visibility_of_element_located((By.XPATH,"//*[@id=\"main_column\"]"))))
            # //*[@id="main_column"]/div[1]/div/div[18]/div/div/div[5]
            
            try:
            	browser.find_element_by_class_name("headline-default")
            	offers_to_send_request.at[index, 'request_sent'] = 100
            	continue
            except:
            	print('This post still exists.')
            
            try:
                nachricht_button    = browser.find_element_by_xpath("//*[@id=\"main_column\"]/div[1]/div/div[18]/div/div/div[5]/a")
                link = nachricht_button.get_attribute('href')
            except:
                print('Page deactivated.')
                offers_to_send_request.at[index, 'request_sent'] = 9
                continue

            print('initializing the message page in %d sec...' % (nap))
            time.sleep(nap)
            browser.get(link)

            browser.implicitly_wait(5)
            parent_h = browser.current_window_handle
            handles = browser.window_handles  # before the pop-up window closes
            # browser.remove(parent_h)
            browser.switch_to_window(handles.pop())
            browser.implicitly_wait(5)  # seconds
            try:
                browser.find_element_by_xpath('//*[@id=\"sicherheit_bestaetigung\"]').click()
            except:
                print('No pop-up.')
            browser.switch_to_window(parent_h)
                #//*[@id="sicherheit_bestaetigung"]

            try:
                browser.implicitly_wait(5)
                browser.find_element_by_id("nachricht-text").send_keys(application)

                browser.implicitly_wait(5)
                select = Select(browser.find_element_by_name('u_anrede'))
                browser.implicitly_wait(5)
                select.select_by_visible_text('Frau')


                browser.implicitly_wait(5)
                browser.find_element_by_name("vorname").send_keys('Wang')

                browser.implicitly_wait(5)
                browser.find_element_by_name("nachname").send_keys('Sally')

                browser.implicitly_wait(5)
                browser.find_element_by_name("email").send_keys('wangsally814@gmail.com')

                browser.implicitly_wait(5)
                try:
                    browser.find_element_by_id('send_message_button').send_keys('\n')
                    browser.implicitly_wait(10)
                    offers_to_send_request.at[index, 'request_sent'] = 1
                    offers_to_send_request.to_csv(csv_file_name_fullinfo, index=False)
                    message_sent += 1
                    print('%d messages has been sent.' % (message_sent))
                except Exception as e:
                    print (e)

            except:
                print('Error entering values and sending message.')
                continue


        except TimeoutException:
            print ("Time out waiting for the page to load")
            continue

    else:
        continue

browser.quit()

print("All offers are looped through.")
