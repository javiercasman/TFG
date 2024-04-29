from skimage import exposure
from skimage.exposure import match_histograms
import cv2 as cv
import numpy as np

def match_brightness_and_contrast(image1, image2):
    # Convertir las imágenes a escala de grises
    gray1 = cv.cvtColor(image1, cv.COLOR_BGR2GRAY)
    gray2 = cv.cvtColor(image2, cv.COLOR_BGR2GRAY)

    # Calcular el brillo y el contraste de cada imagen
    mean1, std1 = cv.meanStdDev(gray1)
    mean2, std2 = cv.meanStdDev(gray2)

    # Ajustar el brillo y el contraste de la primera imagen para que coincida con el de la segunda
    alpha = float(std2 / std1)
    beta = float(mean2 - alpha * mean1)
    adjusted_image = cv.convertScaleAbs(image1, alpha=alpha, beta=beta)

    return adjusted_image

def resize_aspect_ratio(image, new_width):
    width = image.shape[1]
    w_diff = new_width - width
    border = w_diff // 2
    print(border)
    bordered_image = cv.copyMakeBorder(image, 0, 0, border, border, cv.BORDER_CONSTANT, value=(0,0,0))
    return bordered_image, border

frames = 0
fps = 24
width, height = 854, 480
video = cv.VideoCapture("flame.mp4")
source = cv.imread("candle-flame.jpg")
source, border = resize_aspect_ratio(source, width)
while video.isOpened():
    ret, frame = video.read()
    if not ret:
        print("ERROR: No se ha podido leer el frame.\n")
        break
    frames += 1

    resized_frame = cv.resize(frame, (width,height), interpolation=cv.INTER_LINEAR)     # Reescalado a 854x480

    if(frames == 1):
        matched = match_histograms(source,resized_frame,channel_axis=-1)
        cropped_matched = matched[::,border:-border]
        cv.imwrite("matched_flame.jpg", cropped_matched)
        cv.imwrite("frame.jpg", frame)
        cv.imshow('frame', resized_frame)
        cv.imshow('source', source)
        cv.imshow('matched', cropped_matched)
    if cv.waitKey(100000000) & 0xFF == ord('q'):
        break
    video.release()
    cv.destroyAllWindows()
    break