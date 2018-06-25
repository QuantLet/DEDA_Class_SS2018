import subprocess
import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import Image
import ImageDraw
import ImageFont
import json
import urllib2
 
# Raspberry Pi pin configuration:
RST = 24
 
# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
 
# Initialize library.
disp.begin()
 
# Clear display.
disp.clear()
disp.display()
 
# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
 
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
 
# Load default font.
# font = ImageFont.load_default()
# font = ImageFont.truetype('Ubuntu-M.ttf', 14)
fontsmall = ImageFont.truetype('Ubuntu-M.ttf', 16)
fontmedium = ImageFont.truetype('Ubuntu-M.ttf', 14)
fontlarge = ImageFont.truetype('Ubuntu-M.ttf', 16)
 
# Display Image
disp.image(image)
disp.display()
 
# definitions
timerTime = time.time()
 
from time import sleep
 
 
# import requests, json
 
 
# def getBitcoinPrice():
#	URL = 'https://www.bitstamp.net/api/ticker/'
#	try:
#		r = requests.get(URL)
#		priceFloat = float(json.loads(r.text)['last'])
#		return priceFloat
#	except requests.ConnectionError:
#		print "Error querying Bitstamp API"
 
 
 
while True:
 
 
time.sleep(2)
draw.rectangle((0, 0, width, height), outline=0, fill=0)
 
# now = time.time()


#Load requests via pip!
#$ sudo pip install requests



#import urllib.request, json 
#with urllib.request.urlopen("http://thecrix.de/data/crix_hf.json") as url:
#    data = json.loads(url.read().decode())[-10:]


#def last_n_crix_values(n):
# with urllib.request.urlopen("http://thecrix.de/data/crix_hf.json") as url:
#     data = json.loads(url.read().decode())[-n:]
#return data


#import urllib.request, json
#import pandas as pd
#def last_n_crix_values(n):
#    with urllib.request.urlopen("http://thecrix.de/data/crix_hf.json") as url:
#        data = json.loads(url.read().decode())[-n:]
#    return data
#pd.DataFrame(last_n_crix_values(2)).values



#import urllib.request, json
#import pandas as pd
#def last_n_crix_values(n):
#    with urllib.request.urlopen("http://thecrix.de/data/crix_hf.json") as url:
#        data = json.loads(url.read().decode())[-n:]
#    return data
#d = last_n_crix_values(2)
#print(pd.DataFrame(d).values)
#print([i['date'] for i in d])
#print([i['price'] for i in d])
#print([[i['date'],i['price']] for i in d])


import urllib.request, json
import pandas as pd


def last_n_crix_values(n):
	with urllib.request.urlopen("http://thecrix.de/data/crix_hf.json") as url:
		data = json.loads(url.read().decode())[-n:]
	return data


d = last_n_crix_values(2)
pd.DataFrame(d).values
ddate = [i['date'] for i in d]
pprice = [i['price'] for i in d]
#[[i['date'], i['price']] for i in d]


draw.text((1,26), str('Date - ') + str(ddate), font=fontsmall, fill=255)
draw.text((1,1), str(i['ddate'] for i in d) + ' /', font=fontlarge, fill=255)
draw.text((1,48), str('Price - ') + str(pprice), font=fontsmall, fill=255)
draw.text((64,1), ' ' + str(i['pprice'] for i in d), font=fontlarge, fill=255)

sleep(1)
 
disp.image(image)
disp.display()

