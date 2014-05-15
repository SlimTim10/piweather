#!/usr/bin/python

# Author: SlimTim10 <slimtim10@gmail.com>
# Created: 14 May 2014

# The MIT License (MIT)

# Copyright (c) 2014 SlimTim10

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# A fun little project to show the weather on a LCD character display with a Raspberry Pi.
# View README.md for details.

import RPi.GPIO as GPIO
import time
import urllib
import re

# Set a pin on the LCD high or low
def setpin(p, b):
        if p == 'RS':
                GPIO.output(4, b)
        elif p == 'RW':
                GPIO.output(17, b)
        elif p == 'E':
                GPIO.output(22, b)
        else:
                print "Error: invalid pin"

# Put a byte on the LCD data port
def port(d):
        GPIO.output(23, ((d & 0x10) > 0))
        GPIO.output(24, ((d & 0x20) > 0))
        GPIO.output(25, ((d & 0x40) > 0))
        GPIO.output(27, ((d & 0x80) > 0))

# Transfer 4 bits to/from the LCD
def nybble():
        setpin('E', 1)
        time.sleep(0.002)
        setpin('E', 0)

# Send a command to the LCD
def command(d):
        port(d)
        setpin('RS', 0)
        setpin('RW', 0)
        nybble()
        port(d << 4)
        nybble()

# Send a byte of data to the LCD
def data(d):
        port(d)
        setpin('RS', 1)
        setpin('RW', 0)
        nybble()
        port(d << 4)
        nybble()

# Write a string (up to 8 characters) to line 1 or 2 of the LCD
def write(line, s):
        if line == 1:
                command(0x80)
        else:
                command(0xC0)
        i = 0
        for c in s:
                data(ord(c))
                i += 1
        while i < 8:
                data(0x20)
                i += 1

# Clear LCD
def lcd_clear():
        command(0x01)

# Turn LCD cursor off
def lcd_cursor_off():
        command(0x0C)

# Initialize LCD
def init():
        port(0)
        time.sleep(1)
        port(0x30)
        time.sleep(0.01)
        nybble()
        time.sleep(0.01)
        nybble()
        time.sleep(0.01)
        nybble()
        time.sleep(0.01)
        port(0x20)
        nybble()
        command(0x28)
        command(0x10)
        command(0x0F)
        command(0x06)

#GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) # Refer to P1 pins by GPIO number

# Set up GPIOs to interface with LCD
GPIO.setup(4, GPIO.OUT)         # LCD RS
GPIO.setup(17, GPIO.OUT)        # LCD R/W
GPIO.setup(22, GPIO.OUT)        # LCD E
GPIO.setup(23, GPIO.OUT)        # LCD DB4
GPIO.setup(24, GPIO.OUT)        # LCD DB5
GPIO.setup(25, GPIO.OUT)        # LCD DB6
GPIO.setup(27, GPIO.OUT)        # LCD DB7

# Ensure GPIO cleanup when script is ended by SIGINT (Ctrl-C)
try:
        while True:
                init()
                init() # Single init() seems to often fail
                init()

                lcd_clear()
                lcd_cursor_off() # Cursor looks ugly

                # Initialize with "?" in case regex fails
                curtemp = "?"
                hitemp = "?"
                conditions = "?"
                #forecast = "?"

                page = urllib.urlopen("http://weather.gc.ca/city/pages/on-143_metric_e.html").read()

                try:
                        curtemp = re.search("<p class=\"temperature\">(.+)&deg;", page).group(1)        # Current temperature
                except:
                        pass

                try:
                        m = re.findall("<li class=\"high\".*>(.*)&.*;", page)
                        hitemp = m[0] # Other days should be m[1:8]
                except:
                        pass

                try:
                        conditions = re.findall("weathericons.*alt=\"(.*)\" title", page)
                        conditions = "Now: " + conditions[0] + ". Later: " + conditions[1] + "."
                        # Short forecast
                        #conditions = conditions[0] + " " + conditions[1]
                        #if re.search("([Rr]ain)|([Ss]hower)", conditions):
                        #        forecast = "Rain"
                        #elif re.search("([Ss]now)|([Ff]lurries)", conditions):
                        #        forecast = "Snow"
                        #elif re.search("[Cc]loud", conditions):
                        #        forecast = "Cloud"
                        #elif re.search("[Ss]un", conditions):
                        #        forecast = "Sun"
                except:
                        pass

                # Line 1 shows current temperature and high (if available)
                # (e.g., "16 H19" for currently 16, high of 19)
                line1 = curtemp[:2]
                if hitemp:
                        line1 += " H" + hitemp[:2]
                write(1, line1)

                # Line 2 shows current condition and later (same day) condition
                # (e.g., "Now: Cloudy. Later: Showers.")
                line2 = conditions

                print line1 # Debug
                print line2 # Debug

                # Scroll long line
                if len(line2) > 8:
                        starttime = time.time()
                        while time.time() < starttime + 60: # Stop after 60 seconds to recheck weather
                                tmp = line2
                                write(2, tmp[:8])
                                time.sleep(1)
                                while tmp:
                                        tmp = tmp[1:]
                                        write(2, tmp[:8])
                                        time.sleep(0.2) # Adjust for scrolling speed
                else:
                        write(2, line2)
                        time.sleep(60) # Recheck weather after 60 seconds

except KeyboardInterrupt:
        print "Stopping"

finally:
        GPIO.cleanup()
