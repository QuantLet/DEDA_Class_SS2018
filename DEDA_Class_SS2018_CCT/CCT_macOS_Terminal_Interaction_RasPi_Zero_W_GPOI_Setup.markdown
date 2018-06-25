#Headless Setup of Raspberry Pi Zero W (Raspberry Pi 3 Wireless) (macOS)

1. **Formatt the Micro SD card** - Open a terminal and type 'diskutil list'. Find your card and copy the disk name (For example: /dev/disk4). Format the card with `diskutil eraseDisk ExFat temp disk4(Use your disk here)`
2. **Download Raspbian** - `wget https://downloads.raspberrypi.org/raspbian_lite_latest`
3. **Unmount the SD card** - `diskutil unmountDisk /dev/disk4` or whatever your disk path is
4. **Mount the Raspbian image to the card** - `sudo dd if=PATH-TO-RASPBIAN-IMAGE` of=/dev/disk4` or whatever your disk path is 
5. **Enable SSH on the Pi** - `cd /volumes && ls`. You should see a boot partition from the SD card `cd boot && touch ssh`
6. **Setup WiFi on the PI** -  While still in the boot partition of the card type `nano wpa_supplicant.conf` and enter `network={ ssid="YOUR-SSID" psk="YOUR-WIFI-PASSWORD" }`
7. **Boot the PI** - Unmount the card `diskutil unmountDisk /dev/disk4` (or whatever your disk path is) and put it in the Pi, then power up the Pi
8. **SSH Into the Pi** - Find the Pi's IP on your network by running `arp -a` or using an app like LanScan and ssh into it `ssh pi@YOUR_PIS-IP`. THe default password is `raspberry`
9. **Add your SSH key to the PI** - While in the Pi run `install -d -m 700 ~/.ssh`. On you machine run `cat ~/.ssh/id_rsa.pub | ssh <USERNAME>@<IP-ADDRESS> 'cat >> .ssh/authorized_keys'`
