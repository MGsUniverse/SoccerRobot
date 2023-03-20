# USAGE
# python ball_tracking.py --video ball_tracking_example.mp4
# python ball_tracking.py

# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
import time
import socket
from threading import Thread
import nanocamera as nano
import RPi.GPIO as GPIO
from motor import *

camera = 0

cam_args = "nvarguscamerasrc sensor_id=0 ! 'video/x-raw(memory:NVMM),width=3280, height=2464, framerate=21/1, format=NV12' ! nvvidconv flip-method=2 ! 'video/x-raw, width=816, height=616' ! nvvidconv ! nvegltransform ! nveglglessink -e"


class robot:

    def __init__(self, cam, camera):

        next_colour = False

        def gstreamer_pipeline(
                capture_width=1280,
                capture_height=720,
                display_width=1280,
                display_height=720,
                framerate=60,
                flip_method=0,
        ):
            return (
                    "nvarguscamerasrc ! "
                    "video/x-raw(memory:NVMM), "
                    "width=(int)%d, height=(int)%d, "
                    "format=(string)NV12, framerate=(fraction)%d/1 ! "
                    "nvvidconv flip-method=%d ! "
                    "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
                    "videoconvert ! "
                    "video/x-raw, format=(string)BGR ! appsink"
                    % (
                        capture_width,
                        capture_height,
                        framerate,
                        flip_method,
                        display_width,
                        display_height,
                    )
            )

        setup_motor()

        # construct the argument parse and parse the arguments
        ap = argparse.ArgumentParser()
        ap.add_argument("-v", "--video",
                        help="path to the (optional) video file")
        ap.add_argument("-b", "--buffer", type=int, default=64,
                        help="max buffer size")
        args = vars(ap.parse_args())

        # define the lower and upper boundaries of the "green"
        # ball in the HSV color space, then initialize the
        # list of tracked points
        colorLower = (0, 150, 150)
        colorUpper = (5, 255, 255)
        pts = deque(maxlen=args["buffer"])

        # keep looping
        grabbed = None
        frame = None
        while True:
            # grab the current frame
            if cam == 0:
                grabbed, frame = camera.read()
            elif cam == 1:
                grabbed = True
                frame = camera.read()

            # if we are viewing a video and we did not grab a frame,
            # then we have reached the end of the video
            if args.get("video") and not grabbed:
                break

            # resize the frame, blur it, and convert it to the HSV
            # color space
            frame = imutils.resize(frame, width=1280)
            # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            cv2.rectangle(frame, (400, 720), (880, 0), (0, 0, 255), 3)

            # construct a mask for the color "green", then perform
            # a series of dilations and erosions to remove any small
            # blobs left in the mask
            mask = cv2.inRange(hsv, colorLower, colorUpper)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            # find contours in the mask and initialize the current
            # (x, y) center of the ball
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)[-2]
            center = None

            # only proceed if at least one contour was found
            if len(cnts) > 0:
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
                # centroid
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                # only proceed if the radius meets a minimum size
                if radius > 15:
                    # draw the circle and centroid on the frame,
                    # then update the list of tracked points
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)

                    # if ball is on the sides of the camera, move so it's in the center
                    if x < 400:
                        next_colour = False
                        left(0)
                    elif x > 880:
                        next_colour = False
                        right(0)
                    else:
                        # if ball is in the center of the camera, move forwards
                        next_colour = True
                        if cam == 1:
                            forward(0)
                        if cam == 0:
                            backward(0)
                else:
                    # if no ball is found and ball wasn't previously in the center, stop. Otherwise, look for green circle.
                    if next_colour:
                        colorLower = (75, 100, 75)
                        colorUpper = (90, 250, 250)
                    stop(0)

            # update the points queue
            pts.appendleft(center)

            # loop over the set of tracked points
            for i in range(1, len(pts)):
                # if either of the tracked points are None, ignore
                # them
                if pts[i - 1] is None or pts[i] is None:
                    continue

                # otherwise, compute the thickness of the line and
                # draw the connecting lines
                thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
                cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

            # show the frame to our screen
            cv2.imshow("Frame" + str(cam), frame)
            key = cv2.waitKey(1) & 0xFF

            # if the 'q' key is pressed, stop the loop
            if key == ord("q"):
                stop(0)
                break

        # cleanup the camera and close any open windows
        camera.release()
        cv2.destroyAllWindows()


def camera():
    bot = robot(1, nano.Camera(flip=0, width=1280, height=720, fps=30))


t2 = Thread(target=camera)

t2.start()
