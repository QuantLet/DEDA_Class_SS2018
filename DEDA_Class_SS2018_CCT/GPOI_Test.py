# blink.py
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)

while True:
    GPIO.output(7,True)
    time.sleep(0.2)
    GPIO.output(7,False)
    time.sleep(0.2)



    import os
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
 
text = (("Raspberry Pi ", (255, 0, 0)), ("and ", (0, 255, 0)), ("Adafruit", (0, 0, 255)))
 
font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 16)
all_text = ""
for text_color_pair in text:
    t = text_color_pair[0]
    all_text = all_text + t
 
print(all_text)
width, ignore = font.getsize(all_text)
print(width)
 
 
im = Image.new("RGB", (width + 30, 16), "black")
draw = ImageDraw.Draw(im)
 
x = 0;
for text_color_pair in text:
    t = text_color_pair[0]
    c = text_color_pair[1]
    print("t=" + t + " " + str(c) + " " + str(x))
    draw.text((x, 0), t, c, font=font)
    x = x + font.getsize(t)[0]
 
im.save("test.ppm")
 
os.system("./led-matrix 1 test.ppm")




import urllib, json
url = "http://maps.googleapis.com/maps/api/geocode/json?address=google"
response = urllib.urlopen(url)
data = json.loads(response.read())
print data


import urllib.request, json 
with urllib.request.urlopen("http://maps.googleapis.com/maps/api/geocode/json?address=google") as url:
    data = json.loads(url.read().decode())
    print(data)