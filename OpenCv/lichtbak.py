#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import cv2
import imutils
import datetime
import time
import argparse
import saveData
#-------IMAGE SOURCE----------------------------------------------------------------------------------------------------------------------------------------------------
# Use Camera
im = cv2.VideoCapture(0)

# Use Video
#im = cv2.VideoCapture("/Users/Carl/Desktop/ocv/video3.mp4")

#-------VARIABLES----------------------------------------------------------------------------------------------------------------------------------------------------
keyvar = False #Light detected true or false
bikestatus = False #movement detected true or false

countedbike = False
countedbikeandlight = False

light = False
bike = False

bikes = 0
bikeandlight = 0

motioncounter = 0.0 #datetime.datetime.now()
motionnow = 0.0 #datetime.datetime.now()
motiondifference = 0.0 #datetime.datetime.now()
motionlast = 0.0

lightcounter = 0.0 #datetime.datetime.now()
lightnow = 0.0 #datetime.datetime.now()
lightdifference = 0.0 #datetime.datetime.now()
lightlast = 0.0


#-------PARAMETERS BLOB DETECTION---------------------------------------------------------------------------------------------------------------------------------------------------
#Parametres
params = cv2.SimpleBlobDetector_Params()

# Filter by Area.
params.filterByArea = False
params.minArea = 800 #800 300
params.maxArea = 2000 #2000

# Filter by Circularity
params.filterByCircularity = True
params.minCircularity = 0.6 #0.6
params.maxCircularity = 1 #1

# Filter by Convexity
params.filterByConvexity = True
params.minConvexity = 0.9 #0.9
params.maxConvexity = 1 #1

# Filter by Inertia
params.filterByInertia = True
params.minInertiaRatio = 0.71 #0.71 0.5
params.maxInertiaRatio  = 1 #1

#Color of the blob
params.filterByColor = 1 #1
params.blobColor = 255 #255

#-------ARGUMENTS MOTION DETECTION------------------------------------------------------------------------------------------------------------------------------------------------

ap = argparse.ArgumentParser()
ap.add_argument('-a', '--min-area', type=int, default=1500,help='minimum area 2size') #1100 200
args = vars(ap.parse_args())

firstFrame = None

#--------INFITE LOOP-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

while True:
    #mininput = int(input("min: "))
    #maxinput = int(input("max: "))


#-------FRAME CAPTURE---------------------------------------------------------------------------------------------------------------------------------------------------

    # Grabbing Frames
    (grabbed, frame) = im.read()
    if not grabbed:
        break

    # Resizing and COLOR GRAY
    frame = imutils.resize(frame, width=1400)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#-------BLOB DETECTION---------------------------------------------------------------------------------------------------------------------------------------------------

    # Set up the detector with default parameters.
    detector = cv2.SimpleBlobDetector_create(params)

    # Detect blobs.
    keypoints = detector.detect(gray)

    # Draw detected blobs as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    im_with_keypoints = cv2.drawKeypoints(frame, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS) #gray instead of frames


#------MOTION DETECTION---------------------------------------------------------------------------------------------------------------------------------------------------
    #fgbg = cv2.createBackgroundSubtractorMOG2()
    bikestatus = False
    motion = cv2.GaussianBlur(gray, (21, 21), 0)
    #motion = fgbg.apply(frame)
    if firstFrame is None:
        firstFrame = motion
        continue

    # compute the absolute difference between the current frame and
    # first frame
    frameDelta = cv2.absdiff(firstFrame, motion)
    thresh = cv2.threshold(frameDelta, 25, 0xFF, cv2.THRESH_BINARY)[1]

    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=1)
    (img, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)

    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < args['min_area']:
            continue
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(im_with_keypoints, (x, y), (x + w, y + h), (0xFF, 0xFF, 0), 2)
        bikestatus = True

#------BIKE DETECTION AND LIGHT DETECTION---------------------------------------------------------------------------------------------------------------------------------------------------
    #MOTION CHECKER
    if bikestatus:
        #bikestatus = True
        motioncounter = datetime.datetime.now()
        motiondifference = -(motionnow - motioncounter).total_seconds()

    else:
        #bikestatus = False
        motionnow = datetime.datetime.now()

    #LIGHT CHECKER
    if keypoints :
        keyvar = True
        lightcounter = datetime.datetime.now()
        lightdifference = -(lightnow - lightcounter).total_seconds()

    else:
        keyvar = False
        lightnow = datetime.datetime.now()



    # MOTION COMPARISON RESETTER
    if motiondifference > 1:
        bike = True
        #cv2.imwrite('/Users/Carl/Desktop/ocv/image1.png',im_with_keypoints)
        if motionlast == motiondifference:
            bike = False
            countedbike = False
            countedbikeandlight = False
            motiondifference = 0.0
        motionlast = motiondifference

    # LIGHT COMPARISON AND RESETTER
    if lightdifference > 1:
        light = True
        if lightlast == lightdifference:
            light = False
            countedbike = False
            countedbikeandlight = False
            lightdifference = 0.0
        lightlast = lightdifference

    if bike == True and light == True and countedbikeandlight == False:
        bikeandlight += 1
        #saveData.addBiker(ed1)
        countedbikeandlight = True
        countedbike = True
    elif bike == True and countedbike == False:
        bikes += 1
        #saveData.addBiker(1)
        countedbike = True



#-------OUTPUTS--------------------------------------------------------------------------------------------------------------------------------------------------

    #MOTION DETECTION TEXT
    cv2.putText(im_with_keypoints,'Motion Status: {}'.format(bikestatus),(10, 20),cv2.FONT_HERSHEY_DUPLEX,0.5,(255, 255,0),1)
    cv2.putText(im_with_keypoints,'Motion time: {}'.format(motiondifference),(10, 40),cv2.FONT_HERSHEY_DUPLEX,0.5,(255, 255,0),1)
    cv2.putText(im_with_keypoints,'Bike: {}'.format(bike),(550, 20),cv2.FONT_HERSHEY_DUPLEX,0.5,(255, 255,0),1)

    #LIGHT DETECTION TEXT
    cv2.putText(im_with_keypoints, "Light Status: {}".format(keyvar), (10, 60),cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 0xFF), 1)
    cv2.putText(im_with_keypoints, "Light Time: {}".format(lightdifference), (10, 80),cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 0xFF), 1)
    cv2.putText(im_with_keypoints,'Light: {}'.format(light),(550, 40),cv2.FONT_HERSHEY_DUPLEX,0.5,(0, 0, 0xFF),1)

    #DATE
    cv2.putText(im_with_keypoints,datetime.datetime.now().strftime('%A %d %B %Y %I:%M:%S%p'),(10, frame.shape[0] - 10),cv2.FONT_HERSHEY_DUPLEX,0.35,(0, 255, 255),1,)

    cv2.putText(im_with_keypoints,'bikes: {}'.format(bikes),(550, 60),cv2.FONT_HERSHEY_DUPLEX,0.5,(0, 0, 0xFF),1)
    cv2.putText(im_with_keypoints,'Bikes + lights: {}'.format(bikeandlight),(550, 80),cv2.FONT_HERSHEY_DUPLEX,0.5,(0, 0, 0xFF),1)

    # Show Frame
    cv2.imshow("Main", im_with_keypoints)
    #cv2.imshow("gray", motion)
    #cv2.imshow('Thresh', thresh)
    #cv2.imshow('Frame Delta', frameDelta)



#-------CLOSING--------------------------------------------------------------------------------------------------------------------------------------------------
    # if the `q` key is pressed, break from the lop
    key = cv2.waitKey(1) & 0xFF
    firstFrame = motion
    if key == ord('q') or key == ord('Q') :
        break


im.release()
cv2.destroyAllWindows()
