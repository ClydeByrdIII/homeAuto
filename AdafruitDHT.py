#!/usr/bin/python

import socket
import json
import time
import Adafruit_DHT
from client import *

sensor = Adafruit_DHT.DHT22
pin = "P8_11"

ip = '35.2.116.95'
name = 'temp_BBB'

While True:

	did_rec = False
	did = ''
	# get did
	while did_rec == False:

		did = register_client(ip, name)
		if did != '':
	    	did_rec = True
	    	print did
	# Try to grab a sensor reading.  Use the read_retry method which will retry up
	# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
	humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

	#convert the temperature to Fahrenheit.
	temperature = temperature * 9/5.0 + 32

	# Note that sometimes you won't get a reading and
	# the results will be null (because Linux can't
	# guarantee the timing of calls to read the sensor).  
	# If this happens try again!
	if humidity is not None and temperature is not None:
		msg = 'Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity)
		print msg
		if temperature > 70:
			notify_client(ip, did, name, msg)
	time.sleep(5)

