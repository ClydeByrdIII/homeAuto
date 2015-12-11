#!/usr/bin/python

import socket
import json
import time
import threading
import SocketServer
import Adafruit_DHT
from client import *

sensor = Adafruit_DHT.DHT22
pin = "P8_11"

ip = '35.2.116.95'
name = 'temp_BBB'

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

class ThreadedDeviceRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        
        dev_data = self.request.recv(1024)
        data = json.loads(dev_data);

        print self.request.getpeername()

        if data['type'] == 'D_COMMAND':
            if data['command'] == 'DELETE':
                delete_command()
                response = create_status('OK', '')
            else:
                response = create_status('FAIL', 'command "' + data['command'] + '" was not found')
        else:
            response = create_status('FAIL', 'type "' + data['type'] + '" was not found')

        message = json.dumps(response)
        
        print '%s : %s' % ('Response is ', message)
        self.request.send(message)
        return

class ThreadedDeviceServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == '__main__':

    my_ip = get_ip_address()
    port = 5050
    print 'IPADDR:' + my_ip + ' on Port:' + str(port) 
    address = (my_ip, port) # let the kernel give us a port
    server = ThreadedDeviceServer(address, ThreadedDeviceRequestHandler)
    server.allow_reuse_address = True

    t = threading.Thread(target=server.serve_forever)
    t.setDaemon(True) # don't hang on exit
    t.start()
    print 'Server loop running in thread:', t.getName()

    while True:

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
    	time.sleep(10)

