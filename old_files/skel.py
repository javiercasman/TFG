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
    ret,thresh = cv.threshold(gray_frame,100,255,cv.THRESH_BINARY)
    # thresh = cv.GaussianBlur(thresh, (0,0), sigmaX=3, sigmaY=3, 
    #                              borderType = cv.BORDER_DEFAULT)
    cv.imshow('Binary', thresh)
    skel = skeletonize(thresh)
    skel_image = img_as_ubyte(skel)
    

    fil = FilFinder2D(skel_image, distance=250 * u.pc, mask=skel_image)
    fil.preprocess_image(flatten_percent=85)
    fil.create_mask(border_masking=True, verbose=False, use_existing_mask=True)
    fil.medskel(verbose=False)
    fil.analyze_skeletons(branch_thresh=8 * u.pix, skel_thresh=10 * u.pix, 
                          prune_criteria='length')
    
    cv.imshow('Skeleton', skel_image)
    # plt.imshow(skel_image, cmap='gray')
    # plt.axis('off')
    # plt.show()
    # plt.imshow(fil.skeleton, cmap='gray')
    # plt.contour(fil.skeleton_longpath, colors='r')
    # plt.axis('off')
    # plt.show()
    for filament in fil.filaments:
        pixels = filament.branch_properties.get("pixels")
        branch = max(pixels, key=len)
        #print(branch)
        # branch = max(x for x in pixels)
        # for x,y in branch:
        #     print(x,y)
    # branch = max(x for x in fils)
    # print(branch)
    main_branch = np.zeros_like(skel_image)
    for pix in branch:
        main_branch[pix[0], pix[1]] = 255
        
    #AHORA CORNER HARRIS PARA LOS QUE NOS DAN PROBLEMAS (aplicar filtro para no comprobar todos?)
    corners = cv.cornerHarris(main_branch,2,5,0.1)
    corners = cv.dilate(corners, None) #borrar luego?
    main_branch[corners>0.01*corners.max()]=0
    cv.imshow('mask', main_branch)
    print(frames) 
    
    if cv.waitKey(1) & 0xFF == ord('q'):
        break
print(frames)
video.release()
cv.destroyAllWindows()

# ret,thresh = cv.threshold(img,70,255,cv.THRESH_BINARY)
# # cv.imshow('Grayscale Image', thresh)
# # cv.waitKey(0)

# skel = skeletonize(thresh)


# fig,axes = plt.subplots(nrows=1,ncols=3,figsize = (8,4),
#                         sharex=True, sharey=True)
# ax = axes.ravel()
# ax[0].imshow(img,cmap=plt.cm.gray)
# ax[0].axis('off')
# ax[0].set_title('original', fontsize=20)

# ax[1].imshow(thresh,cmap=plt.cm.gray)
# ax[1].axis('off')
# ax[1].set_title('binarized', fontsize=20)

# ax[2].imshow(skel, cmap=plt.cm.gray)
# ax[2].axis('off')
# ax[2].set_title('skeleton', fontsize=20)

# fig.tight_layout()
# plt.show()
# # (244,296)
# # (202,336)
# # (277,326)
# # (244,168)

