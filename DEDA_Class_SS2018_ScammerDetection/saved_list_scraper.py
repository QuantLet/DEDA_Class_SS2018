from bs4 import BeautifulSoup

import os.path
import glob
import pandas as pd



def clean_text(text):
	text = text.replace(' ' , '').replace('\n', '')
	text = text.replace('€' , 'euros')
	text = text.replace('m²' , 'squaremeter')
	text = text.replace('ä' , 'ae').replace('Ä' , 'Ae')
	text = text.replace('ö' , 'oe').replace('Ö' , 'Oe')
	text = text.replace('ü' , 'ue').replace('Ü' , 'Ue')                                                    
	return text

def get_entrag(entrag_element):
	try:
		entrag = entrag_element.find('span').text
		return clean_text(entrag)
	except:
		return 'empty'

def get_miete(miete_element):
	try:
		miete = miete_element.find('span').text
		return clean_text(miete)
	except:
		return 'empty'

def get_groesse(groesse_element):
	try:
		groesse = groesse_element.find('span').text
		return clean_text(groesse)
	except:
		return 'empty'

def get_stadtteil(stadtteil_element):
	try:
		stadtteil = stadtteil_element.find('span').text
		return clean_text(stadtteil)
	except:
		return 'empty'

def get_freiab(freiab_element):
	try:
		freiab = freiab_element.find('span').text
		return freiab
	except:
		return 'empty'

def get_freibis(freibis_element):
	try:
		freibis = freibis_element.find('span').text
		return freibis
	except:
		return 'empty'

def get_bewohner(bewohner_element):
	try:
		num_bewohner_weiblich = len(bewohner_element.find_all('img', {'alt': 'weiblich'}))
		num_bewohner_mannlich = len(bewohner_element.find_all('img', {'alt': 'männlich'}))
		num_egal_mitbewohner_gesucht = len(bewohner_element.find_all('img', {'alt': 'Mitbewohnerin oder Mitbwohner gesucht'}))
		num_mitbewohner_gesucht = len(bewohner_element.find_all('img', {'alt': 'Mitbewohner gesucht'}))
		num_mitbewohnerin_gesucht = len(bewohner_element.find_all('img', {'alt': 'Mitbewohnerin gesucht'}))
				
		return num_bewohner_mannlich, num_bewohner_weiblich, \
		num_egal_mitbewohner_gesucht, num_mitbewohner_gesucht, num_mitbewohnerin_gesucht
		
	except:
		return 'empty', 'empty'
	
def get_offer_link(element):
	try:
		link = str(element.find('a')['href'])
		return link
	except:
		return 'empty'

#def write_offer_to_csv(csv_file, offer_list):
# a function to write the scraped offer into the csv file prepared
#	with open(csv_file, 'w') as f:
#		writer = csv.writer(f)
#		writer.writerow(offer_list)
#	print('written offer into csv!')

def scrap_list_page(page_html, df):
# a function to scrape all information of the flat offers in the list page
	soup_obj = BeautifulSoup(page_html, 'lxml')
	
	eintrag_list = soup_obj.find_all('td', {'class': 'ang_spalte_datum row_click'})
	miete_list = soup_obj.find_all('td', {'class': 'position-relative ang_spalte_miete row_click'})
	groesse_list = soup_obj.find_all('td', {'class': 'ang_spalte_groesse row_click'})
	stadtteil_list = soup_obj.find_all('td', {'class': 'ang_spalte_stadt row_click'})
	freiab_list = soup_obj.find_all('td', {'class': 'ang_spalte_freiab row_click'})
	freibis_list = soup_obj.find_all('td', {'class': 'ang_spalte_freibis row_click'})
	bewohner_list = soup_obj.find_all('td', {'class': 'ang_spalte_icons row_click'})


	print('%d offers are found' % (len(stadtteil_list)))
	
	for i in range(0,len(stadtteil_list)):
		if (get_stadtteil(stadtteil_list[i]).find('ImmobilienScout24') == -1)\
		and (get_stadtteil(stadtteil_list[i]).find('Airbnb') == -1):	### CHECK
			eintrag 	= get_entrag(eintrag_list[i])
			miete 		= get_miete(miete_list[i])
			groesse 	= get_groesse(groesse_list[i])
			stadtteil 	= get_stadtteil(stadtteil_list[i])
			freiab 		= get_freiab(freiab_list[i])
			freibis 	= get_freibis(freibis_list[i])
			link 		= get_offer_link(eintrag_list[i])
			a,b,c,d,e	= get_bewohner(bewohner_list[i])
						
			offer_list = [eintrag, miete, groesse, stadtteil, freiab, freibis, \
			int(a), int(b), int(c), int(d), int(e), link]
			
#			write_offer_to_csv(csv_file_name, offer_list)
			df_row = pd.DataFrame([offer_list])
			df_row.columns = ['eintrag','miete','groesse','stadtteil','freiab','freibis','bewohner_M',\
	'bewohner_W','freiraum_egal','freiraum_M','freiraum_W','link']
			df = pd.concat([df, df_row])
			
		else:
			continue
		
	return df
	
	
# path for stored html documents of list pages
project_directory 	= '/Users/jessiehsieh/Documents/Programming/Data_Science/WebScraping/WGgesucht/'

path = 'manual_HTML/ListPage/*.htm'

csv_file_name 		= project_directory + 'wggesucht_angebote.csv'

#with open(csv_file_name, 'w') as f:

column_names = ['eintrag','miete','groesse','stadtteil','freiab','freibis','bewohner_M',\
	'bewohner_W','freiraum_egal','freiraum_M','freiraum_W','link']


# a loop to check all saved html in the ListPage folder
for file_name in glob.iglob(path):
    with open(file_name) as f:
        page_html = f.read()

        offers = pd.DataFrame(columns = column_names)
        offers = pd.concat([offers, scrap_list_page(page_html, offers)])
	
        if not (os.path.isfile('wggesucht_angebote.csv')):
            offers.to_csv(csv_file_name, index=False)
            print('New csv file saved')
        else:
            existing_offers = pd.read_csv(csv_file_name)
            all_offers = pd.concat([existing_offers, offers])
            all_offers = all_offers.drop_duplicates()
            all_offers.to_csv(csv_file_name, index=False)
            print('offers added to existing csv file')