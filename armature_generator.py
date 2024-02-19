import numpy as np
from skimage.morphology import skeletonize
from skimage import img_as_ubyte
import cv2 as cv
from plantcv import plantcv as pcv
import math

def tab_writer(i):      # Ayuda a generar las tabulaciones en el fichero '.bvh'
    for k in range(i+1):
        f.write("\t")

frames = 0
fps = 24
k = 5       # N-1 bones, afegim un extra

f = open("armature.bvh", "w")
f.write("HIERARCHY\nROOT Bone\n{\n")

video = cv.VideoCapture('D:\\TFG\\TFG\\flame.mp4')
while video.isOpened():
    ret, frame = video.read()
    if not ret:
        break

    frames += 1
    if(frames == 207):
        continue        # Eliminamos este frame manualmente, se resiste al tratamiento

    resized_frame = cv.resize(frame, (854, 480), interpolation=cv.INTER_LINEAR)     # Reescalado a 854x480
    gray_frame = cv.cvtColor(resized_frame, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(gray_frame,110,255,cv.THRESH_BINARY)

    skel = skeletonize(thresh)
    skel_image = img_as_ubyte(skel)
#    cv.imshow('Skeleton', skel_image)          Descomentar para mostrar el esqueleto original sin tratar
    pruned_skeleton, segmented_img, segment_objects = pcv.morphology.prune(skel_img=skel_image, size=60)        # Primera pruna de ramas innecesarias, sobretodo las de la parte superior del esqueleto

    corners = cv.cornerHarris(pruned_skeleton,2,27,0.02)        # Detección de las esquinas de la(s) pata(s) inferior(es)
    corners = cv.dilate(corners, None)        # Dilatación de las esquinas detectadas para facilitar su eliminación

    pruned_skeleton[corners>0.01*corners.max()] = 0        # Esquinas del esqueleto pintadas de negro, patas separadas
    segmented_img, segment_objects = pcv.morphology.segment_skeleton(skel_img=pruned_skeleton)      # Dividimos el esqueleto en segmentos una vez separadas las patas
    longest_segment = max(segment_objects, key=len)        # Cogemos el segmento más largo, es decir, el vertical, del cual generaremos los huesos
    N = (len(longest_segment) / 2) + 1
    longest_segment = longest_segment[:int(N)]        # Por algún motivo, el segmento devuelto por la función tiene la forma [x0y0, x1y1, ..., xn-1yn-1, xnyn, xn-1yn-1, xn-2yn-2, ..., x1y1], con esto cogemos directamente la mitad de la lista, es decir 
                                                      # el segmento entero sin píxeles duplicados
    
    branch = np.zeros_like(pruned_skeleton)        # Nueva imagen negra del mismo tamaño que el esqueleto tratado, donde 'pintaremos' la rama deseada
    for [pixel] in longest_segment:
        branch[pixel[1], pixel[0]] = 255        # Pintamos los píxeles del segmento
    base = [400,429] 
    branch[base[0],base[1]] = 255        # Pintamos un píxel fijo para todos los frames, representará el orígen del armature (mecha)

    n_pixels = len(longest_segment)
    last, first = np.flip(longest_segment[0][0]), np.flip(longest_segment[-1][0])
    length = base[0] - last[0]
    step = int(n_pixels/k)
    points = []        # Guardaremos los puntos para los huesos
    for i in range(1,k):
        points.insert(0,np.flip(longest_segment[step*i][0]))        # Dividimos el segmento en k partes
    points.append(last)
    points.insert(0,first)
    points.insert(0,base)

    if frames == 1:        # En el primer frame calculamos los offsets
        escala = 0.8/length        # La llama en Blender mide ~0.8m, escalaremos las distancias
        last_point_x, last_point_z = base[0], base[1]
        for i in range(k+2):
            point = points[i]
            offset_z, offset_x = (last_point_x - point[0]) * escala, (last_point_z - point[1]) * escala
            tab_writer(i)
            f.write("OFFSET {:.6f}".format(offset_x) + " {:.6f}".format(0) + " {:.6f}".format(offset_z) + "\n")           # Escribimos en el fichero '.bvh'
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

                last_point_x, last_point_z = point[0], point[1]
            else:
                for j in range(1,k+3):
                    tab_writer(i-j)
                    f.write("}\n")
        f.write("MOTION\n")
        f.write("Frames: ")         # Esta linea la modificaremos más adelante, cuanto tengamos el conteo de frames
        f.write("Frame Time: {:.6f}\n".format(1/fps))

    f.write("{:.6f} ".format(0) + "{:.6f} ".format(0) + "{:.6f} ".format(0))        # XYZposition del primer hueso, en nuestro caso será 0 siempre ya que la base no se mueve
    for i in range(k+1):
        point1, point2 = points[i], points[i+1]
        delta_x, delta_y = point1[0] - point2[0], point1[1] - point2[1]
        rads = np.arctan2(delta_y, delta_x)
        degrees = np.degrees(rads)
        rotation = degrees
        if i > 0:
            rotation -= last_degrees
        f.write("{:.6f} ".format(0) + "{:.6f} ".format(rotation) + "{:.6f} ".format(0))          # Rotación en Y
        last_degrees = degrees         # Para calcular los grados necesitamos la referencia del anterior punto
    f.write("\n")

#    cv.imshow('skeleton', branch)
#    if cv.waitKey(1) & 0xFF == ord('q'):
#        break                                # Descomentar estas tres para imprimir cada frame del esqueleto después del procesamiento

video.release()
cv.destroyAllWindows()
f.close()
f = open("armature.bvh", "r")
lines = f.readlines()
for i, line in enumerate(lines):
    if line.startswith("Frames:"):
        lines[i] += "{}".format(frames-1) + "\n"        # Modificamos esta línea una vez tenemos los frames contados
f.close()
f = open("armature.bvh", "w")
f.writelines(lines)