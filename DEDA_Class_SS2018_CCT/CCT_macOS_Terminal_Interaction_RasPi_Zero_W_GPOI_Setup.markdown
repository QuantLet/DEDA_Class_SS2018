**MacOS GPOI Setup of Raspberry Pi Zero W for use with CCT setup**

1. **Formatt the Micro SD card**
Open a terminal and type 'diskutil list'. Find your card and copy the disk name (For example mine is: /dev/disk2). 
Format the card with `diskutil eraseDisk ExFat temp disk2(Use your disk here)`



1. **relog to the RasPi** and load the essentials
`pi@raspberrypi:~ $ sudo apt-get update 
pi@raspberrypi:~ $ sudo apt-get install build-essential python-dev python-pip pi@raspberrypi:~ $ sudo pip install RPi.GPIO
pi@raspberrypi:~ $ sudo apt-get install python-imaging python-smbus`

2. I am using the Adafruit 128x32 PiOLED display https://www.ebay.de/itm/Adafruit-PiOLED-128x32-Monochrom-OLED-Display-Add-on-f%C3%BCr-Raspberry-Pi-3527/253073184075?ssPageName=STRK%3AMEBIDX%3AIT&_trksid=p2057872.m2749.l2649
  **download the Adafruit SSD1306 python library code**
`pi@raspberrypi:~ $ sudo apt-get install git 
pi@raspberrypi:~ $  git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git 
pi@raspberrypi:~ $  cd Adafruit_Python_SSD1306 sudo python setup.py install`

3. **load the i2c package to enable peripherals**
`pi@raspberrypi:~ $ sudo apt-get install -y python-smbus 
pi@raspberrypi:~ $ sudo apt-get install -y i2c-tools`

4. **enable kernel support for peripherals**
`pi@raspberrypi:~ $ sudo raspi-config`
go to #5 Interfacing Options, #A7 i2c, enable, **reboot RasPi prompt**

5. **after reboot, shutdown RasPi**
`pi@raspberrypi:~ $ sudo shutdown -h now`

6. **plug in the peripheral**, here the 128x32 PiOLED display
**test i2c function after reboot/relog**
`pi@raspberrypi:~ $ sudo i2cdetect -y 1`

Between all the hypens, an address like 0x3c should be seen: It works.
Now you can run the PY code.

R2
