#!/usr/bin/python

import json
import time
import socket
import datetime
import picamera
import threading
import subprocess
import SocketServer
import picamera.array
from client import *
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from subprocess import call
from fractions import Fraction

#Constants
SECONDS2MICRO = 1000000  # Constant for converting Shutter Speed in Seconds to Microseconds

# User Customizable Settings
imageWidth = 1980
imageHeight = 1080

threshold = 10  # How Much pixel changes
sensitivity = 100  # How many pixels change

nightISO = 800
nightShutSpeed = 6 * SECONDS2MICRO  # seconds times conversion to microseconds constant

# Advanced Settings not normally changed 
testWidth = 100
testHeight = 75

ip = '35.2.116.95'
name = 'motion_pi'
my_ip = ''

def create_status(status, msg):
    return {'type': 'D_STATUS', 'status': status, 'msg': msg}

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
            elif data['command'] == 'KILL':
                call (["pkill raspivid"], shell=True)
                call (["pkill janus"], shell=True)
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

def takeMotionImage(width, height, daymode):
    with picamera.PiCamera() as camera:
        time.sleep(1)
        camera.resolution = (width, height)
        with picamera.array.PiRGBArray(camera) as stream:
            if daymode:
                camera.exposure_mode = 'auto'
                camera.awb_mode = 'auto' 
            else:
                # Take Low Light image            
                # Set a framerate of 1/6 fps, then set shutter
                # speed to 6s and ISO to 800
                camera.framerate = Fraction(1, 6)
                camera.shutter_speed = nightShutSpeed
                camera.exposure_mode = 'off'
                camera.iso = nightISO
                # Give the camera a good long time to measure AWB
                # (you may wish to use fixed AWB instead)
                time.sleep( 10 )
            camera.capture(stream, format='rgb')
            return stream.array

           
def scanMotion(width, height, daymode):
    motionFound = False
    data1 = takeMotionImage(width, height, daymode)
    while not motionFound:
        data2 = takeMotionImage(width, height, daymode)
        diffCount = 0L;
        for w in range(0, width):
            for h in range(0, height):
                # get the diff of the pixel. Conversion to int
                # is required to avoid unsigned short overflow.
                diff = abs(int(data1[h][w][1]) - int(data2[h][w][1]))
                if  diff > threshold:
                    diffCount += 1
            if diffCount > sensitivity:
                break; #break outer loop.
        if diffCount > sensitivity:
            motionFound = True
        else:
            data2 = data1              
    return motionFound

def motionDetection():
    print "Scanning for Motion threshold=%i sensitivity=%i ......"  % (threshold, sensitivity)
    isDay = True

    while True:
        # get did
        did_rec = False
        did = ''
        # get did
        while did_rec == False:
            did = register_client(ip, name)
            if did != '':
                did_rec = True
                print did
        # do motion detection
        if scanMotion(testWidth, testHeight, isDay):
            print 'Motion Detected'
            notify_client(ip, did, name, 'Motion Detected! Please look at http://' + my_ip +'/demos/webrtc.html')
            vidproc = subprocess.Popen('./makestream.sh', shell=True)
            gateproc = subprocess.Popen('./makegateway.sh', shell=True)
            vidproc.wait()
            gateproc.wait()
            vidproc = None
            gateproc = None
            time.sleep(10)
             
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

    try:
        motionDetection()
    finally:
        print ""
        print "+++++++++++++++"
        print "Exiting Program"
        print "+++++++++++++++" 
        print ""        

    
    
    
