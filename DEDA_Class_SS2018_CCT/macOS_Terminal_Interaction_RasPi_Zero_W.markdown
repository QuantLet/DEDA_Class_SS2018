#Headless Setup of Raspberry Pi Zero W (Raspberry Pi 3 Wireless) (macOS)

1. **Formatt the Micro SD card**
Open a terminal and type 'diskutil list'. Find your card and copy the disk name (For example mine is: /dev/disk2). 
Format the card with `diskutil eraseDisk ExFat temp disk2(Use your disk here)`

2. **Download latest e.g. lite Raspbian** 
`r2$ wget https://downloads.raspberrypi.org/raspbian_lite_latest`

3. insert Micro SD Card for Raspery Pi 
   open terminal
   **get name of your SD card, mine is listed as disk2**
`r2$ diskutil list`

4. **format disk2**
`r2$ eraseDisk ExFat temp disk2`

5. **unmount disk2**
`r2$ diskutil unmountDisk /dev/disk2`

6. **flash OS to disk2**
   divide commands with space; dd=data dupe; sudo=super user do; 
   write until input file if=, then drag and drop the file, then output file of=…, then transfer block size speed, here 4mb (k would be kb=slower), sync command = optional
`r2$ sudo dd if=/Users/r2/Downloads/2018-04-18-raspbian-stretch-lite.img of=/dev/disk2 bs=4m`

7. **enable ssh (Secure Shell) access to RasPi**
   a. **Mac partition list**
`r2$ cd /volumes`
`r2$ ls`

   b. **choose SD card “boot” partition**
`r2$ cd boot`

8. **create ssh “config boot command file”** (option I used) to enable ssh login
  touch command is the easiest way to create new, empty files
`r2$ touch ssh`

9. go to “boot” card in the finder (notepad++ or others not needed on Mac)
   **open cmdline.txt**, and add at the end after a space (**not new line**!!):
`modules-load=dwc2,g_ether`

10. **open config.txt**, and add anywhere **in a new line** (!)
`dtoverlay=dwc2`

11. **create new “Make Plain text”** (Options!) file called **wpa_supplicant.conf** for immediate WiFi access 
   as we are using a Raspberry Pi Zero W, no USB.
   save it with having “If no extension is provided, use txt” unchecked
`ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev 
update_config=1 
country=DE 
network={
  ssid="Networkname" 
  psk="Networkpassword" 
  key_mgmt=WPA-PSK
}`


12. **ping RasPi** to get the IP
`r2$ ping raspberrypi.local`

otherwise use the App “Fing” from the Appstore to scan your network
https://itunes.apple.com/us/app/fing-network-scanner/id430921107?mt=8

13. **login to RasPi**
  a. **method 1 (raspberry.local)**
`r2$ ssh pi@raspberry.local`
  b. **method 2 (IP)**
`r2$ ssh pi@XXX.XXX.X.XXX`

14. logged in to RasPi, “r2$ “ will change to
`pi@raspberrypi:~ $`

15. **enable SD card space for Raspian**
`pi@raspberrypi:~ $ sudo raspi-config`
go to #7 Advanced Options, then #A1 Expand Filesystem, **Reboot** Prompt

16. **ssh relog** to RasPi
update/rebuild packages, enter Y if asked
`pi@raspberrypi:~ $ sudo apt-get update
pi@raspberrypi:~ $ sudo apt-get upgrade`

17. **clear installation packages**
`pi@raspberrypi:~ $ sudo apt-get clean`

18. **edit localization settings** which include language, keyboard, date etc.
  a. **Version 1**
`pi@raspberrypi:~ $ sudo raspi-config`
go to #4 Localization Options and fill out each point
  b. **Version 2**
if your input is not accepted, then run to create a “locale” file
`pi@raspberrypi:~ $ sudo nano /etc/default/locale`
add the following lines to the locale file via the nano editor
GB is the default setting - I’ll keep it
`LANG=en_GB.UTF-8
LC_ALL=en_GB.UTF-8
LANGUAGE=en_GB.UTF-8`

19. **reboot the RasPi**
`pi@raspberrypi:~ $ sudo reboot`

R2
