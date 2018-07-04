import requests
from requests.auth import HTTPBasicAuth

import time
from bs4 import BeautifulSoup
import datetime

import os.path
import csv
import pandas as pd

from random import randint


def clean_text(text):
	text = text.replace(' ' , '').replace('\n', '')
	text = text.replace('€' , 'euros').replace('m²' , 'squaremeter')
	text = text.replace('ä' , 'ae').replace('Ä' , 'Ae')
	text = text.replace('ö' , 'oe').replace('Ö' , 'Oe')
	text = text.replace('ü' , 'ue').replace('Ü' , 'Ue').replace('ß', '')
	text = text.replace('Nebenkosten:' , '').replace('SonstigeKosten:' , '').replace('Kaution:' , '')
	text = text.replace('Abstandszahlung:' ,'').replace('SCHUFA-Auskunft','')
	return text

def clean_spaces(text):
	text = text.replace('€', 'euros').replace('m²', 'squaremeter')
	text = text.replace('\n', '').replace('\r', '')
	for i in range(0, len(text)):
		text = text.replace('  ', '')
	return text

def get_miete_breakdown(soup_obj):

	nebenKosten 	= 'none'
	sonstigeKosten 	= 'none'
	kaution			= 'none'
	abstandszahlung = 'none'
	SCHUFA 			= 'none'	

	try:
		table = soup_obj.find(lambda tag: tag.name == 'table')
		rows = table.findAll(lambda tag: tag.name == 'tr')
		
		for row in rows:
			if 'Nebenkosten' in row.text:
				nebenKosten = clean_text(row.text)
			if 'SonstigeKosten' in row.text:
				sonstigeKosten = clean_text(row.text)
			if 'Kaution' in row.text:
				kaution = clean_text(row.text)
			if 'Abstandszahlung' in row.text:
				abstandszahlung = clean_text(row.text)
			if 'SCHUFA' in row.text:
				SCHUFA = clean_text(row.text)

	except:
		print('Error in getting rent details.')

	return nebenKosten, sonstigeKosten, kaution, abstandszahlung, SCHUFA

def get_address_details(soup_obj):

	division = soup_obj.find('div',{'class': 'col-sm-4 mb10'})
	
	if division:
		
		details = division.findAll('a')

	try:
		address_part1 	= clean_text(details[0].contents[0])
		address_part2 	= clean_text(details[0].contents[2])
		umzugsfirma 	= clean_text(details[1].text)

	except:
		address_part1	= 'none'
		address_part2	= 'none'
		umzugsfirma		= 'none'

	return address_part1, address_part2, umzugsfirma

def get_wohnung_details(soup_obj):
	
	wohnungsgroesse 	= 'none'
	rauchen 			= 'none'
	gesucht				= 'none'
		
	try:
		detail_list = []
		for panel in soup_obj.findAll('ul', {'class': 'ul-detailed-view-datasheet print_text_left'}):
			for li in panel.findAll('li'):
				if li.string:
					detail_list.append(clean_spaces(li.string))
					
		for item in detail_list:
			if 'Wohnungsgröße' in item:
				wohnungsgroesse = item.replace('Wohnungsgröße: ', '')
			if 'Rauchen' in item:
				rauchen = item.replace('Rauchen ', '')
			if ('Frau' in item) or ('Mann' in item):
				gesucht = item.replace('Frau ', '').replace('Mann ', '').replace('oder ', '')

	except:
		print('Error getting WG details.')

	return wohnungsgroesse, rauchen, gesucht

def get_text(soup_obj):
	text_zimmer = ''
	freetexts = soup_obj.findAll('div', {'id': 'freitext_0', 'class': 'freitext wordWrap'})
	try:
		for text in freetexts:
			text_zimmer += text.text
	except:
		print(text_zimmer)

	text_lage = ''
	freetexts = soup_obj.findAll('div', {'id': 'freitext_1', 'class': 'freitext wordWrap'})
	try:
		for text in freetexts:
			text_lage += text.text
	except:
		print(text_lage)

	text_WGleben = ''
	freetexts = soup_obj.findAll('div', {'id': 'freitext_2', 'class': 'freitext wordWrap'})
	try:
		for text in freetexts:
			text_WGlebel += text.text
	except:
		print(text_WGleben)

	text_sonstige = ''
	freetexts = soup_obj.findAll('div', {'id': 'freitext_3', 'class': 'freitext wordWrap'})
	try:
		for text in freetexts:
			text_sonstige += text.text
	except:
		print(text_sonstige)

	return clean_spaces(text_zimmer), clean_spaces(text_lage), \
		   clean_spaces(text_WGleben), clean_spaces(text_sonstige)

def get_membership(soup_obj):
	contact_elements = soup_obj.find('div', {'class': 'hidden-md hidden-lg noprint'})

	MitgliedSeit = 'none'
	flag = 0
	try:
		for div in contact_elements.findAll('div'):
			if div.text == 'Mitglied seit:':
				flag = 1
				continue
			if flag == 1:
				MitgliedSeit = div.text
				break
	except:
		print('membership not found')
	return clean_text(MitgliedSeit)

def extract_offer(offer_link, page_html, column_names):
# a function to scrape all information of the offer details in the offer page
	soup_obj = BeautifulSoup(page_html, 'lxml')

	if len(soup_obj.find_all('form', {'name':"checkform",'method':"post", 'action':"https://www.wg-gesucht.de/cuba.html"}))==0:
		headline = ''
		headline_elements = soup_obj.find_all('span', {'class': 'headlineContent col-xs-12'})
		for element in headline_elements:
			headline += element.text

		nebenKosten, sonstigeKosten, kaution, abstandszahlung, SCHUFA 	= get_miete_breakdown(soup_obj)
		address_part1, address_part2, umzugsfirma 						= get_address_details(soup_obj)
		wohnungsgroesse, rauchen, gesucht 								= get_wohnung_details(soup_obj)
		text_zimmer, text_lage, text_WGleben, text_sonstige				= get_text(soup_obj)
		MitgliedSeit 													= get_membership(soup_obj)
					
		offerinfo_list = [offer_link, headline, nebenKosten, sonstigeKosten, kaution, abstandszahlung, SCHUFA, \
						  address_part1, address_part2, umzugsfirma, wohnungsgroesse, rauchen, gesucht, \
						  text_zimmer, text_lage, text_WGleben, text_sonstige, MitgliedSeit, 0]

		df_row = pd.DataFrame([offerinfo_list])
		
	else:
		print('I am found to be a robot:(')
		df_row = pd.DataFrame([None]*len(column_names))
		
	df_row.columns = column_names
	return df_row

def save_offerpage_html(html_doc, path, link):
# a function to save the list page in html for debug and analysis
	file_name = link.replace('wg-zimmer-in-Berlin','').replace('-','').replace('.','_') + '.html'
	
	file_name_with_path = os.path.join(path, file_name)
	
	file = open(file_name_with_path, 'w')
	
	file.write(html_doc)
	
	file.close()
	
	print("Offer Page %s is saved" % (file_name))

	
# a function to be applied to every link in the offers collection, and calls the scraper functions
def OfferScraper_fromLink(offer_link):

	nap = 62.19625895 + float(randint(0, 9))
	
	try:
		print('initializing the page in %d sec...' % (nap))
		time.sleep(nap)
		# wait a minute until it searches the webpage
		try:
			r = requests.get('https://www.wg-gesucht.de/' + offer_link, auth=HTTPBasicAuth('jazzjassie', 'pass'))
			# package the request, send the request and catch the response
			print('offer page %s obtained' % (offer_link))
		
		except Exception as e:
			print(e)
			print('Retrying after an hour')
			time.sleep(3600)
			r = requests.get(URL)
			
		page_html = r.text
			
	# get the html of the list page
		print('saving offer page...')
		save_offerpage_html(html_doc = page_html, path = saved_html_path, link = offer_link)
		# a function save them for analysis in the future
	
		print('scraping offer page...')
		return extract_offer(offer_link, page_html, column_names)
		
	except Exception as e:
		print(e)
		return pd.DataFrame([None]*len(column_names), columns = column_names)

# path for stored html documents of list pages
project_directory 	= '/Users/jessiehsieh/Documents/Programming/Data_Science/WebScraping/WGgesucht/'

saved_html_path 	= project_directory + 'angeboteHTML/'

csv_file_name			= project_directory + 'wggesucht_angebote.csv'
csv_file_name_fullinfo 	= project_directory + 'wggesucht_angebote_full.csv'

column_names = ['link', 'headline','nebenKosten','sonstigeKosten', 'kaution','abstandszahlung','SCHUFA',\
			   'address_part1','address_part2', 'umzugsfirma','wohnungsgroesse','rauchen','gesucht',\
			   'text_zimmer', 'text_lage', 'text_WGleben', 'text_sonstige', 'MitgliedSeit','request_sent']

offer_content = pd.DataFrame(columns = column_names)

offers_collection = pd.read_csv(csv_file_name).drop_duplicates(subset = ['link'])

if os.path.isfile(csv_file_name_fullinfo):
	existing_offers_full 	= pd.read_csv(csv_file_name_fullinfo)
	offers_collection		= offers_collection[~offers_collection['link'].isin(existing_offers_full['link'])]

for index, row in offers_collection.iterrows():

	# find the details from the webpage
	offer_content = OfferScraper_fromLink(row['link'])
	# join the detail found to the collection
	offer_full = offers_collection.merge(offer_content, on='link', how='inner')

	if not (os.path.isfile(csv_file_name_fullinfo)):
		offer_full.to_csv(csv_file_name_fullinfo, index=False)
		print('New csv file saved.\n')
	else:
		existing_offers_full = pd.read_csv(csv_file_name_fullinfo)
		all_offers = pd.concat([existing_offers_full, offer_full])

		all_offers.to_csv(csv_file_name_fullinfo, index=False)
		print('Offer added to existing csv file.\n')
