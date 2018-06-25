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
 
 
 
	p = 1
        q = 0.026
        # print getBitcoinPrice() / p * q
	# sleep(1)
 
 
	urlusd = 'http://api.coindesk.com/v1/bpi/currentprice/usd.json'
	jsonURLusd=urllib2.urlopen(urlusd)
        jsonObjectusd=json.load(jsonURLusd)
 
 
	
 
	bbl = jsonObjectusd['bpi']['USD']['rate']	
	bitbut = round(jsonObjectusd['bpi']['USD']['rate_float'], 3)
	bbc = round(bitbut / p * q, 2)
 
	
	url="http://api.coindesk.com/v1/bpi/currentprice/GBP.json"
 
	jsonURL=urllib2.urlopen(url)
 
	jsonObject=json.load(jsonURL)
 
	pbl = jsonObject['bpi']['GBP']['rate']
	poundbit = round(jsonObject['bpi']['GBP']['rate_float'], 3)
	pbc = round(poundbit / p * q, 2) 
	
 
 
	# print 'USD Bitcoin Price'
        # print bbl
        # print 'USD Price Calculated'
        # print bbc
 
 
	# print 'GBP Bitcoin Price'
	# print pbl
	# print 'GBP Bitcoin Calculated'
	# print pbc
 
	
 
	draw.text((1,26), str('USD - ') + str(bitbut), font=fontsmall, fill=255)
	draw.text((1,1), str(bbc) + ' /', font=fontlarge, fill=255)
	draw.text((1,48), str('GBP - ') + str(poundbit), font=fontsmall, fill=255)
	draw.text((64,1), ' ' + str(pbc), font=fontlarge, fill=255)
 
	sleep(1)
 
	disp.image(image)
	disp.display()