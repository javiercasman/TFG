from skimage import exposure
from skimage.exposure import match_histograms
import cv2 as cv

frames = 0
fps = 24
length, width = 854, 480
video = cv.VideoCapture("flame.mp4")
source = cv.imread("candle-flame.jpg")
while video.isOpened():
    ret, frame = video.read()
    if not ret:
        print("ERROR: No se ha podido leer el frame.\n")
        break
    frames += 1

    resized_frame = cv.resize(frame, (length,width), interpolation=cv.INTER_LINEAR)     # Reescalado a 854x480

    if(frames == 1):
        matched = match_histograms(source,resized_frame)
        cv.imshow('frame', resized_frame)
        cv.imshow('source', source)
        cv.imshow('matched', matched)
        cv.imwrite("matched_flame.jpg", matched)
    if cv.waitKey(10000) & 0xFF == ord('q'):
        break
    video.release()
    cv.destroyAllWindows()
    break