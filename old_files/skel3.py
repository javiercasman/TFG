import sys
import numpy as np
from skimage.morphology import skeletonize
from skimage import data, img_as_ubyte
import matplotlib.pyplot as plt
from skimage.util import invert
import cv2 as cv
from fil_finder import FilFinder2D
import astropy.units as u
from IPython.display import display
import pandas as pd
from scipy import ndimage
from plantcv import plantcv as pcv

video = cv.VideoCapture('D:\\TFG\\TFG\\flame.mp4')
# img = cv.imread('D:\\TFG\\TFG\\frame.png',0)
frames = 0
while video.isOpened():
    ret, frame = video.read()
    if not ret:
        break
    frames += 1
    resized_frame = cv.resize(frame, (854, 480), interpolation=cv.INTER_LINEAR)
    gray_frame = cv.cvtColor(resized_frame, cv.COLOR_BGR2GRAY)
    ret,thresh = cv.threshold(gray_frame,110,255,cv.THRESH_BINARY)#110
    # thresh = cv.GaussianBlur(thresh, (0,0), sigmaX=3, sigmaY=3, 
    #                              borderType = cv.BORDER_DEFAULT)
    #cv.imshow('Binary', thresh)
    skel = skeletonize(thresh)
    skel_image = img_as_ubyte(skel)
    pixels = []
    for i in range(480):
        for j in range(854):
            if skel_image[i,j] == 255:
                pixels.append((i,j))
    mask = np.zeros_like(skel_image)
    for x,y in pixels[:260]:
        mask[x,y] = 255

    cv.imshow('Skeleton', mask)
    if cv.waitKey(2) & 0xFF == ord('q'):
        break
video.release()
cv.destroyAllWindows()