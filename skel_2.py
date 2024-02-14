import sys
import numpy as np
from skimage.morphology import skeletonize
from skimage import img_as_ubyte
import cv2 as cv
from plantcv import plantcv as pcv
import math

def tab_writer(i):
    for k in range(i+1):
        f.write("\t")

video = cv.VideoCapture('D:\\TFG\\TFG\\flame.mp4')
frames = 0
fps = 24
k = 5 #n of bones - 1, pq le añadimos uno artificial
f = open("skel.bvh", "w")
f.write("HIERARCHY\nROOT Bone\n{\n")
while video.isOpened():
    ret, frame = video.read()
    if not ret:
        break
    frames += 1
    if(frames == 207):
        continue #este frame es imposible de podarlo bien
    resized_frame = cv.resize(frame, (854, 480), interpolation=cv.INTER_LINEAR)
    gray_frame = cv.cvtColor(resized_frame, cv.COLOR_BGR2GRAY)
    ret,thresh = cv.threshold(gray_frame,110,255,cv.THRESH_BINARY)#110

    skel = skeletonize(thresh)
    skel_image = img_as_ubyte(skel)
    #cv.imshow('Skeleton', skel_image)
    pruned_skeleton, segmented_img, segment_objects = pcv.morphology.prune(skel_img=skel_image, size=60)

    corners = cv.cornerHarris(pruned_skeleton,2,27,0.02)
    corners = cv.dilate(corners, None)

    pruned_skeleton[corners>0.01*corners.max()] = 0
    segmented_img, segment_objects = pcv.morphology.segment_skeleton(skel_img=pruned_skeleton)
    longest_segment = max(segment_objects, key=len)
    N = (len(longest_segment) / 2) + 1
    longest_segment = longest_segment[:int(N)]
    branch = np.zeros_like(pruned_skeleton)
    for [pixel] in longest_segment:
        branch[pixel[1], pixel[0]] = 255
    base = [400,429] 
    branch[base[0],base[1]] = 255 #la base de la llama, la cabeza del primer hueso (mecha)

    n_pixels = len(longest_segment)
    last, first = np.flip(longest_segment[0][0]), np.flip(longest_segment[-1][0]) #last arriba, first abajo
    length = base[0] - last[0]
    step = int(n_pixels/k)
    points = []
    for i in range(1,k):
        points.insert(0,np.flip(longest_segment[step*i][0]))
    points.append(last)
    points.insert(0,first)
    points.insert(0,base)

    if frames == 1:#offsets de los huesos
        escala = 0.8/length #la llama en blender mide 0.8, aquí son 323 = length
        last_pointx, last_pointz = base[0], base[1]
        for i in range(k+2):
            point = points[i]
            offsetz, offsetx = (last_pointx - point[0]) * escala, (last_pointz - point[1]) * escala
            tab_writer(i)
            f.write("OFFSET {:.6f}".format(offsetx) + " {:.6f}".format(0) + " {:.6f}".format(offsetz) + "\n")
            if i != 6:
                tab_writer(i)
                if i == 0:
                    f.write("CHANNELS 6 Xposition Yposition Zposition Xrotation Yrotation Zrotation\n")
                else:
                    f.write("CHANNELS 3 Xrotation Yrotation Zrotation\n")
                
                tab_writer(i)
                if i == k:
                    f.write("End Site\n")
                else:
                    f.write("JOINT Bone.00{}".format(i+1) + "\n")

                tab_writer(i)
                f.write("{\n")

                last_pointx, last_pointz = point[0], point[1]
            else:
                for j in range(1,k+3):
                    tab_writer(i-j)
                    f.write("}\n")
        f.write("MOTION\n")
        f.write("Frames: ")#la modificaremos más tarde
        f.write("Frame Time: {:.6f}\n".format(1/fps))

    f.write("{:.6f} ".format(0) + "{:.6f} ".format(0) + "{:.6f} ".format(0))#X,Y,Zposition del primer hueso, en nuestro caso será 0 siempre pq la base no se mueve
    for i in range(k+1):
        point1, point2 = points[i], points[i+1]
        delta_x, delta_y = point1[0] - point2[0], point1[1] - point2[1]
        rads = np.arctan2(delta_y, delta_x)
        degrees = np.degrees(rads)
        f.write("{:.6f} ".format(0) + "{:.6f} ".format(degrees) + "{:.6f} ".format(0))#solo habrá rotación de y
    f.write("\n")

video.release()
cv.destroyAllWindows()
f.close()
f = open("skel.bvh", "r")
lines = f.readlines()
for i, line in enumerate(lines):
    if line.startswith("Frames:"):
        lines[i] += "{}".format(frames-1) + "\n"
f.close()
f = open("skel.bvh", "w")
f.writelines(lines)