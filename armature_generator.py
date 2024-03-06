import numpy as np
from skimage.morphology import skeletonize
from skimage import img_as_ubyte
from skimage.draw import line
from scipy.ndimage import binary_fill_holes
import cv2 as cv
from plantcv import plantcv as pcv
import math

def tab_writer(i):      # Ayuda a generar las tabulaciones en el fichero '.bvh'
    for k in range(i+1):
        f.write("\t")

frames = 0
fps = 24
k = 6       # N bones == N-1 puntos
w = 11      # N-1 puntos (== N anillos) para calcular amplada

write_file = False   # Booleano para determinar si queremos ejecutar el código escribiendo el .bvh o no

length, width = 854, 480

if write_file:
    f = open("armature.bvh", "w")
    f.write("HIERARCHY\nROOT Bone\n{\n")

base = [0]
video = cv.VideoCapture('flame.mp4')
while video.isOpened():
    ret, frame = video.read()
    if not ret:
        break

    frames += 1
#    if(frames == 207):
#        continue        # Eliminamos este frame manualmente, se resiste al tratamiento

    resized_frame = cv.resize(frame, (length,width), interpolation=cv.INTER_LINEAR)     # Reescalado a 854x480
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

    if not all(base):
        base = np.flip(longest_segment[-1][0].copy())
        while thresh[base[0]][base[1]] > 0:
            base[0] += 1
    rows, cols = line(longest_segment[-1][0][1], longest_segment[-1][0][0], base[0], base[1])
    branch[rows,cols] = 255
    seg = list(zip(cols[1:], rows[1:]))
    for a in seg:
        arr = np.asarray(a).reshape(1,2)
        longest_segment = np.insert(longest_segment, longest_segment.shape[0], arr, axis=0)

    # Puntos de los huesos:
    n_pixels = len(longest_segment)
    last, first = np.flip(longest_segment[0][0]), np.flip(longest_segment[-1][0])
    segment_length = first[0] - last[0]
    step = int(n_pixels/k)
    points = []        # Guardaremos los puntos para los huesos
    for i in range(1,k):
        points.insert(0,np.flip(longest_segment[step*i][0]))        # Dividimos el segmento en k+1 partes
    points.append(last)
    points.insert(0,first)

    if write_file:
        if frames == 1:        # En el primer frame calculamos los offsets
            escala = 0.8/segment_length        # La llama en Blender mide ~0.8m, escalaremos las distancias
            last_point_x, last_point_z = first[0], first[1]
            for i in range(k+1):
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
                    if i == k-1:
                        f.write("End Site\n")
                    else:
                        f.write("JOINT Bone.00{}".format(i+1) + "\n")

                    tab_writer(i)
                    f.write("{\n")

                    last_point_x, last_point_z = point[0], point[1]
                else:
                    for j in range(1,k+2):
                        tab_writer(i-j)
                        f.write("}\n")
            f.write("MOTION\n")
            f.write("Frames: \n")         # Esta linea la modificaremos más adelante, cuanto tengamos el conteo de frames
            f.write("Frame Time: {:.6f}\n".format(1/fps))

        f.write("{:.6f} ".format(0) + "{:.6f} ".format(0) + "{:.6f} ".format(0))        # XYZposition del primer hueso, en nuestro caso será 0 siempre ya que la base no se mueve
        for i in range(k):
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

    contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    max_contour = max(contours, key=cv.contourArea)
    convex_hull = cv.convexHull(max_contour)
    thresh_ch = np.zeros_like(thresh)
    cv.drawContours(thresh_ch, [convex_hull], 0, 255, -1)

    # Puntos para calcular la anchura (w)
    last, first = longest_segment[0][0], longest_segment[-1][0]
    step = int(n_pixels/w)
    points_w = []
    for i in range(1,w):
        points_w.insert(0,longest_segment[step*i][0])
    points_w.append(last)
    points_w.insert(0,first)
#    points_w.insert(0,base)

    for i in range(w+1):
        if i < w: point1, point2 = points_w[i], points_w[i+1] 
        else: point1, point2 = points_w[i], points_w[i-1]
        m = (point2[1] - point1[1]) / (point2[0] - point1[0])
        m_perpendicular = -1 / m if m != 0 else np.inf
        x1,y1 = point1

        x_perpendicular = x1
        y_perpendicular = y1 + m_perpendicular  * (x_perpendicular - x1)
        while True:
            if thresh_ch[int(y_perpendicular), int(x_perpendicular)] == 0:
                x_perpendicular -= 1
                y_perpendicular = y1 + m_perpendicular  * (x_perpendicular - x1)
                break
            x_perpendicular += 1
            y_perpendicular = y1 + m_perpendicular  * (x_perpendicular - x1)

        cv.line(branch, point1, (int(x_perpendicular), int(y_perpendicular)), 255)      # Hacia derecha

        x_perpendicular = x1
        y_perpendicular = y1 + m_perpendicular  * (x_perpendicular - x1)
        while True:
            if thresh_ch[int(y_perpendicular), int(x_perpendicular)] == 0:
                x_perpendicular += 1
                y_perpendicular = y1 + m_perpendicular  * (x_perpendicular - x1)
                break
            x_perpendicular -= 1
            y_perpendicular = y1 + m_perpendicular  * (x_perpendicular - x1)

        cv.line(branch, point1, (int(x_perpendicular), int(y_perpendicular)), 255)      # Hacia izquierda
    
    #flame = cv.cvtColor(thresh_ch, cv.COLOR_GRAY2BGR)
    flame = gray_frame
    sk, _ = cv.findContours(branch, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cv.drawContours(flame, sk, -1, (0, 0, 255), 1)

    # cv.imshow('skeleton', branch)
    # cv.imshow('thresh',thresh)
    # cv.imshow('hull',thresh_ch)
    # cv.imshow('gray',gray_frame)
    cv.imshow('flame',flame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break                                # Descomentar estas tres para imprimir cada frame del esqueleto después del procesamiento

video.release()
cv.destroyAllWindows()

if write_file:
    f.close()

    f = open("armature.bvh", "r")
    lines = f.readlines()
    for i, line in enumerate(lines):
        if line.startswith("Frames:"):
            lines[i] = "Frames: {}".format(frames) + "\n"        # Modificamos esta línea una vez tenemos los frames contados
    f.close()
    f = open("armature.bvh", "w")
    f.writelines(lines)