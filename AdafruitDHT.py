#!/usr/bin/python
# Copyright (c) 2014 Adafruit Industries

import sys
import Adafruit_DHT


# Try to grab a sensor reading.  Use the read_retry method which will retry up
# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
sensor = Adafruit_DHT.DHT22
pin = "P8_11"
humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

convert the temperature to Fahrenheit.
temperature = temperature * 9/5.0 + 32

# Note that sometimes you won't get a reading and
# the results will be null (because Linux can't
# guarantee the timing of calls to read the sensor).  
# If this happens try again!
if humidity is not None and temperature is not None:
	print 'Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity)
else:
	print 'Failed to get reading. Try again!'
	sys.exit(1)
