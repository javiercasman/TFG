from skimage import exposure
from skimage.exposure import match_histograms
import numpy as np
import colour
import cv2 as cv
import sys
np.set_printoptions(threshold=sys.maxsize)

def rgb_to_kelvin(rgb):
    # Coeficientes para calcular la temperatura de color basada en el balance de blancos
    r, g, b = rgb
    r /= 255.0
    g /= 255.0
    b /= 255.0
    
    # Fórmula para calcular la temperatura de color en grados Kelvin
    kelvin = - 25599 * (r * r) - 15582 * (g * g) + 28430 * (b * b) + 29351 * r + 40519 * g - 7755 * b + 6500

    return kelvin

frames = 0
fps = 24
width, height = 854, 480
video = cv.VideoCapture("flame.mp4")
source = cv.imread("candle-flame.jpg")
while video.isOpened():
    ret, frame = video.read()
    if not ret:
        print("ERROR: No se ha podido leer el frame.\n")
        break
    frames += 1
    resized_frame = cv.resize(frame, (width,height), interpolation=cv.INTER_LINEAR)     # Reescalado a 854x480

    if(frames == 1):
        gris = cv.cvtColor(resized_frame, cv.COLOR_BGR2GRAY)
        _, thresh = cv.threshold(gris, 35, 255, cv.THRESH_BINARY) 
        contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        if contours:
            mascara = np.zeros_like(gris)
            cv.drawContours(mascara, contours, -1, (255), thickness=cv.FILLED)
        _, thresh = cv.threshold(gris, 235, 255, cv.THRESH_BINARY) #nos quedamos con los píxeles menores a 235
        contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        mask = cv.bitwise_not(thresh)
        no_white = cv.bitwise_and(mascara, mascara, mask=mask)
        imagen_procesada = cv.bitwise_and(resized_frame, resized_frame, mask=no_white)

        pixels_no_black = cv.findNonZero(no_white)
        mean_cct = 0
        mean_cct2 = 0
        count = 0
        for pixel in pixels_no_black:
            x, y = pixel[0]
            b,g,r = imagen_procesada[y,x]
            rgb = np.array([r,g,b])
            xyz = colour.sRGB_to_XYZ(rgb / 255)
            xy = colour.XYZ_to_xy(xyz)
            cct = colour.xy_to_CCT(xy, 'hernandez1999')
            mean_cct += cct
            count += 1
        mean_cct /= count
        print(mean_cct)

        cv.imshow("original", resized_frame)
        cv.imshow("mask", no_white)
        cv.imshow("procesada",imagen_procesada)
    if cv.waitKey(10000000) & 0xFF == ord('q'):
        break
    video.release()
    cv.destroyAllWindows()
    break