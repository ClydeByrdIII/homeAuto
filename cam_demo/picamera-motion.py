#!/usr/bin/python

verbose = True
if verbose:
    print "Loading python libraries ....."
else:
    print "verbose output has been disabled verbose=False"

import picamera
import picamera.array
import datetime
import time
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from fractions import Fraction

#Constants
SECONDS2MICRO = 1000000  # Constant for converting Shutter Speed in Seconds to Microseconds

# User Customizable Settings
imageDir = "images"
imagePath = "/home/pi/pimotion/" + imageDir
imageNamePrefix = 'capture-'  # Prefix for all image file names. Eg front-
imageWidth = 1980
imageHeight = 1080
imageVFlip = False   # Flip image Vertically
imageHFlip = False   # Flip image Horizontally
imagePreview = False

numberSequence = False

threshold = 10  # How Much pixel changes
sensitivity = 100  # How many pixels change

nightISO = 800
nightShutSpeed = 6 * SECONDS2MICRO  # seconds times conversion to microseconds constant

# Advanced Settings not normally changed 
testWidth = 100
testHeight = 75

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
    currentCount= 1000
    while True:
        if scanMotion(testWidth, testHeight, isDay):
            print 'Motion Detected'
            raw_input()
             
if __name__ == '__main__':
    try:
        motionDetection()
    finally:
        print ""
        print "+++++++++++++++"
        print "Exiting Program"
        print "+++++++++++++++" 
        print ""        

    
    
    
