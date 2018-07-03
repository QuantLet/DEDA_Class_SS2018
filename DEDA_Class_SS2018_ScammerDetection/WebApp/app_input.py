import pandas as pd
import warnings
warnings.filterwarnings('ignore')
from sklearn.ensemble import RandomForestClassifier
from textblob_de import TextBlobDE as TextBlobDE

from flask import Flask, flash, redirect, render_template, request, session, abort
from random import randint
 
app = Flask(__name__)

def clean_text(text):
    text = text.lower().replace('\n', '')
    text = text.replace('€' , 'euros').replace('m²' , 'squaremeter')
    text = text.replace('ä' , 'ae').replace('Ä' , 'Ae')
    text = text.replace('ö' , 'oe').replace('Ö' , 'Oe')
    text = text.replace('ü' , 'ue').replace('Ü' , 'Ue').replace('ß', 'ss')
    return text

def data_prep_to_predict(eintrag, freiab, freibis, mitgliedseit, miete, groesse, area, text):
	
	keywords = ['möbliert','unmöbliert','bitte','leider','Skype','besichtigung','xx',':\)']
	# features to prepare:
	column_list = ['miete_delta','groesse','days_to_freiab','days_to_rent','polarity_de',\
	'popular_area','new_user'] + keywords

	# popular_area and miete_delta
	areas = ['kreuzberg', 'wedding','neukoelln','charlottenburg','mitte','friedrichshain','prenzlauerberg','moabit']
	popular_area = 0
	miete_delta = miete-436
	if clean_text(area) in areas:
		popular_area = 1
		miete_delta = miete-470
		
	#days_to_freiab
	days_to_freiab = abs((freiab - eintrag).days)
	
	#days_to_rent
	days_to_rent = abs((freibis - freiab).days)
	
	#polarity_de
	polarity_de = TextBlobDE(text).polarity
	
	#new_user
	new_user = 0
	if abs((eintrag - mitgliedseit).days) < 30:
		new_user = 1
	else:
		None
	#keyword features
	keyword_features = []
	for word in keywords:
		if word in text:
			keyword_features.append(1)
		else:
			keyword_features.append(0)
			
	feature_list = [miete_delta, groesse, days_to_freiab, days_to_rent, polarity_de,\
	popular_area, new_user] + keyword_features
	
	features = pd.DataFrame(feature_list).T
	features.columns = column_list
	
	return features

def train_model():
	train_data = pd.read_csv('/Users/jessiehsieh/Documents/Programming/Data_Science/WebScraping/WGgesucht/train_data.csv')
	keywords = ['möbliert','unmöbliert','bitte','leider', 'Skype','besichtigung','xx', ':\)']
	feature_list = ['miete_delta','groesse', 'days_to_freiab', 'days_to_rent'\
                   ,'polarity_de', 'popular_area', 'new_user'] + keywords
	
	RF_model = RandomForestClassifier(random_state=123456, n_estimators=15, \
	min_samples_leaf = 2, max_depth = 5, oob_score=True, class_weight = 'balanced')
	RF_model.fit(train_data[feature_list], train_data['scam'])
	return RF_model

@app.route('/')
def index():    
    return render_template('input.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
	# All these try-except statements are to make sure entries are input correctly.
	try:
		date_posted = pd.to_datetime(request.form['date_posted'])
		try:
			freiab = pd.to_datetime(request.form['freiab'])
			try:
				freibis = pd.to_datetime(request.form['freibis'])
				try:
					mitgliedseit = pd.to_datetime(request.form['mitgliedseit'])
					try:
						miete = int(request.form['miete'])
						try:
							#groesse = int(request.form['groesse'])
							groesse = 20
							area = request.form['area']
							text = request.form['full_text']
							# up to this, all inputs are parsed correctly, then
							try:
								features 	= data_prep_to_predict(date_posted,freiab,freibis,mitgliedseit,\
								miete, groesse, area, text)
								pred_model 	= train_model()
								try:
									proba 		= pred_model.predict_proba(features.values.reshape(1,-1))[:, 1][0]
									# .values.reshape(1,-1) to be added if the features is a DF
									return 'The offer you entered is {}% similar to a scam.'.format(str(round(proba*100)))
								except Exception as e:
									print(e)
									return 'Prediction failed!!'
								
							except Exception as e:
								print(e)
								return 'Feature extraction failed!'
						except:
							return 'Incorrect input for room size! Please only enter integer.'
					except:
						return 'Incorrect input for rent! Please only enter integer.'
				except:
					return 'Incorrect input for month of membership!'
			except:
				return 'Incorrect input for date to stay til!'
		except:
			return 'Incorrect input for date starting rent!'
	except:
		return 'Incorrect input for date posted!'
 
if __name__ == "__main__":
#	app.debug = True
	app.run(host='0.0.0.0', port=80)