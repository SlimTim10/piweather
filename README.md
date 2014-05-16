piweather
====================

A fun little project to show the weather on a LCD character display with a Raspberry Pi.

## Hardware
- [Raspberry Pi model B Rev2](http://www.raspberrypi.org)
- [2x8 character LCD module](http://www.newhavendisplay.com/nhd0208azrnybw33v-p-5156.html) ([datasheet](http://www.newhavendisplay.com/specs/NHD-0208AZ-RN-YBW-33V.pdf))

## OS
- [Raspbian](http://www.raspbian.org/) (2013-02-09-wheezy-raspbian)

## Software
- Python 2.7.3
 - [RPi.GPIO](https://pypi.python.org/pypi/RPi.GPIO) (ships with Raspbian)

## Wiring
| Raspberry Pi P1 Header | LCD |
| ---: | :--- |
| (3.3 V) 1 | 2 (VDD) |
| (GND) 6 | 1 (VSS) |
| (GPIO 4) 7 | 4 (RS) |
| (GPIO 17) 11 | 5 (R/W) |
| (GPIO 22) 15 | 6 (E) |
| (GPIO 23) 16 | 11 (DB4) |
| (GPIO 24) 18 | 12 (DB5) |
| (GPIO 25) 22 | 13 (DB6) |
| (GPIO 27) 13 | 14 (DB7) |

LCD pin 3 (V0) has a 1.5K ohm resistor connected to ground for the LCD's contrast.

## Description
This python script scrapes the [GC weather forecast page for Toronto, ON](http://weather.gc.ca/city/pages/on-143_metric_e.html) for the temperature and weather conditions to display the information on a LCD display (and update once every 5 minutes). [Other cities in Canada](http://weather.gc.ca/canada_e.html) work as well, but for a different weather website, the regex will have to be changed. The code comments may be lacking because this was a personal project.

#### Example weather display:
```
16 H19
Now: Cloudy. Later: Showers.
```
The first line means "currently 16, high of 19 today". The second line will be scrolling because it is longer than the LCD.

## Recommended Setup
The following setup starts piweather.py on boot and allows you to SSH in to terminate it (and shutdown), which means you only need to provide power and networking to the Raspberry Pi.

1. Clone piweather.py into the home directory (e.g., /home/pi/).
2. Make the script executable:

        chmod 755 /home/pi/piweather.py

3. Create a symbolic link to the script in /etc/init.d/:

        sudo ln -s /home/pi/piweather.py /etc/init.d/piweather

4. Register script to be run on boot:

        sudo update-rc.d piweather defaults 98

5. Register SSH to be run on boot:

        sudo update-rc.d ssh defaults

To end the script safely in SSH:

    sudo pkill -SIGTERM piweather

## Additional Information
####To set up Wi-Fi to connect on boot:
```
sudo apt-get update
sudo apt-get install wicd-curses
sudo wicd curses

Press 'P' for preferences
Set Wireless Interface: wlan0
Press F10 to save
Press 'R' to refresh
Navigate to your network
Press right arrow to configure
Select 'Automatically connect to this network'
Set Key: <wireless password>
Press F10 to save
Press 'C' to connect

Edit /etc/network/interfaces to include: auto wlan0
```