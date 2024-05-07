import numpy as np
from skimage.morphology import skeletonize
from skimage import img_as_ubyte, exposure
from skimage.exposure import match_histograms
from skimage.draw import line as sk_line
from scipy.ndimage import binary_fill_holes as binary_fill_holes
import cv2 as cv
from plantcv import plantcv as pcv
import math
import bpy
import colour
import os

def tab_writer(i,f):      # Ayuda a generar las tabulaciones en el fichero '.bvh'
    for _ in range(i+1):
        f.write("\t")

def resize_aspect_ratio(image, new_width):
    width = image.shape[1]
    w_diff = new_width - width
    border = w_diff // 2
    bordered_image = cv.copyMakeBorder(image, 0, 0, border, border, cv.BORDER_CONSTANT, value=(0,0,0))
    return bordered_image, border


def generate_armature(flame_video_name, n_bones, n_rings, 
                      view_gray, view_binary, view_skel_raw, view_skel_treated, view_flame_skel):
    # dir = (os.path.abspath(os.path.join(bpy.path.abspath("//"), os.pardir))) #//TFG
    dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)) #//TFG
    #dir = (os.path.abspath(os.path.join(os.getcwd(), os.pardir))) #//TFG
    #dir = (os.path.abspath(os.path.join(dir, os.pardir))) 
    video_path = dir + ("\\") + flame_video_name
    if os.path.exists(video_path):
        flame_name = flame_video_name.split('.')[0]
        n_bones_n_rings = str(n_bones) + "_" + str(n_rings)
        directory =  dir + ("//") + "flames" + ("//") + flame_name + ("//") + n_bones_n_rings       # La carpeta se llamará XXXXX (el video es XXXXX.mp4)
        bvh_file_path = directory + ("//") + "Armature_" + flame_name + ".bvh"
        cfg_file_path = directory + ("//") + "Config_" + flame_name + ".cfg"
        flame_mh_path = directory + ("//") + "candle-flame_" + flame_name + ".jpg"
        write_armature_file = not(os.path.exists(bvh_file_path))
        write_config_file = not(os.path.exists(cfg_file_path))
        generate_flame_mh = not(os.path.exists(flame_mh_path))
        execute = write_armature_file or write_config_file or generate_flame_mh or view_gray or view_binary or view_skel_raw or view_skel_treated or view_flame_skel
        if execute:
            n_rings -= 1 # Para no tener que cambiar todo el código
            if not os.path.exists(directory):
                os.makedirs(directory)
            frames = 0
            fps = 24
            width, height = 854, 480
            if write_armature_file:
                f = open(bvh_file_path, "w")
                f.write("HIERARCHY\nROOT Bone\n{\n")
            if write_config_file:
                f1 = open(cfg_file_path, "w")

            base = [0]
            video = cv.VideoCapture(video_path)
            while video.isOpened():
                ret, frame = video.read()
                if not ret:
                    print("ERROR: No se ha podido leer el frame.\n")
                    break
                frames += 1

                resized_frame = cv.resize(frame, (width,height), interpolation=cv.INTER_LINEAR)     # Reescalado a 854x480
                
                gray_frame = cv.cvtColor(resized_frame, cv.COLOR_BGR2GRAY)

                if(frames == 1):
                    if(generate_flame_mh):
                        source = cv.imread(dir + ("//") + "candle-flame.jpg")
                        source, border = resize_aspect_ratio(source, width)
                        matched = match_histograms(source,resized_frame,channel_axis=-1)
                        cropped_matched = matched[::,border:-border]
                        cv.imwrite(flame_mh_path, cropped_matched)

                    if(write_config_file):
                        _, thresh = cv.threshold(gray_frame, 35, 255, cv.THRESH_BINARY) 
                        contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

                        if contours:
                            mascara = np.zeros_like(gray_frame)
                            cv.drawContours(mascara, contours, -1, (255), thickness=cv.FILLED)
                        _, thresh = cv.threshold(gray_frame, 200, 255, cv.THRESH_BINARY) #nos quedamos con los píxeles menores a 235
                        contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
                        mask = cv.bitwise_not(thresh)
                        no_white = cv.bitwise_and(mascara, mascara, mask=mask)
                        imagen_procesada = cv.bitwise_and(resized_frame, resized_frame, mask=no_white)

                        pixels_no_black = cv.findNonZero(no_white)
                        temperature = 0
                        count = 0
                        for pixel in pixels_no_black:
                            x, y = pixel[0]
                            b,g,r = imagen_procesada[y,x]
                            rgb = np.array([r,g,b])
                            xyz = colour.sRGB_to_XYZ(rgb / 255)
                            xy = colour.XYZ_to_xy(xyz)
                            cct = colour.xy_to_CCT(xy, 'hernandez1999')
                            temperature += cct
                            count += 1
                        temperature /= count

                ## SKELETONIZE ##

                ret, thresh = cv.threshold(gray_frame,100,255,cv.THRESH_BINARY)
                
                contours, _ = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
                max_contour = max(contours, key=cv.contourArea)
                convex_hull = cv.convexHull(max_contour)
                cv.drawContours(thresh, [convex_hull], 0, 255, -1)

                skel = skeletonize(thresh)
                skel_image = img_as_ubyte(skel)

                corners = cv.cornerHarris(skel_image,30,27,0.015)        # Detección de las esquinas de la(s) pata(s) inferior(es)
                #32 27 0.02
                #corners = cv.dilate(corners, None)        # Dilatación de las esquinas detectadas para facilitar su eliminación

                pruned_skeleton = skel_image.copy()
                pruned_skeleton[corners>0.01*corners.max()] = 0

                _, segment_objects = pcv.morphology.segment_skeleton(skel_img=pruned_skeleton)      # Dividimos el esqueleto en segmentos una vez separadas las patas

                # pruned_skeleton, _, segment_objects = pcv.morphology.prune(skel_img=skel_image, size=60)        # Primera pruna de ramas innecesarias, sobretodo las de la parte superior del esqueleto               

#                if frames == 90:
#                    cv.imwrite("D:\\TFG\\MEMORIA\\test\\90_pruned.png", pruned_skeleton)



                # pruned_skeleton[corners>0.01*corners.max()] = 0        # Esquinas del esqueleto pintadas de negro, patas separadas

                # borrar, segment_objects = pcv.morphology.segment_skeleton(skel_img=pruned_skeleton)      # Dividimos el esqueleto en segmentos una vez separadas las patas
                # #longest_segment = max(segment_objects, key=len)        # Cogemos el segmento más largo, es decir, el vertical, del cual generaremos los huesos #CAMBIAR POR EL SEGMENTO QUE ESTÁ MÁS ARRIBA
                longest_segment = min(segment_objects, key=lambda x: np.min(x[0][0][1])) # Cogemos el segmento más arriba

                N = (len(longest_segment) / 2) + 1
                longest_segment = longest_segment[:int(N)]        # Por algún motivo, el segmento devuelto por la función tiene la forma [x0y0, x1y1, ..., xn-1yn-1, xnyn, xn-1yn-1, xn-2yn-2, ..., x1y1], con esto cogemos directamente la mitad de la lista, es decir 
                #                                                 # el segmento entero sin píxeles duplicados
                
                branch = np.zeros_like(pruned_skeleton)        # Nueva imagen negra del mismo tamaño que el esqueleto tratado, donde 'pintaremos' la rama deseada
                for [pixel] in longest_segment:
                    branch[pixel[1], pixel[0]] = 255        # Pintamos los píxeles del segmento

                if not all(base):       # Generar punto base, se hará en el primer frame
                    base = np.flip(longest_segment[-1][0].copy())
                    count = 0
                    while thresh[count+base[0]][base[1]] > 0:
                        count += 1
                    base[0] += int(count/2)

                rows, cols = sk_line(longest_segment[-1][0][1], longest_segment[-1][0][0], base[0], base[1])
                branch[rows,cols] = 255
                seg = list(zip(cols[1:], rows[1:]))
                for a in seg:
                    arr = np.asarray(a).reshape(1,2)
                    longest_segment = np.insert(longest_segment, longest_segment.shape[0], arr, axis=0)

                # Puntos de los bones (armature):
                n_pixels = len(longest_segment)
                last, first = np.flip(longest_segment[0][0]), np.flip(longest_segment[-1][0])
                segment_length = first[0] - last[0]
                step = int(n_pixels/n_bones)
                points = []        # Guardaremos los puntos para los huesos
                for i in range(1,n_bones):
                    points.insert(0,np.flip(longest_segment[step*i][0]))        # Dividimos el segmento en n_bones+1 partes
                points.append(last)
                points.insert(0,first)

                escala = 0.8/segment_length        # La llama en Blender mide ~0.8m, escalaremos las distancias
                if write_armature_file:
                    if frames == 1:        # En el primer frame calculamos los offsets
                        last_point_x, last_point_z = first[0], first[1]
                        for i in range(n_bones+1):
                            point = points[i]
                            offset_z, offset_x = (last_point_x - point[0]) * escala, (last_point_z - point[1]) * escala
                            tab_writer(i,f)
                            f.write("OFFSET {:.6f}".format(offset_x) + " {:.6f}".format(0) + " {:.6f}".format(offset_z) + "\n")           # Escribimos en el fichero '.bvh'
                            if i != n_bones:
                                tab_writer(i,f)
                                if i == 0:
                                    f.write("CHANNELS 6 Xposition Yposition Zposition Xrotation Yrotation Zrotation\n")
                                else:
                                    f.write("CHANNELS 3 Xrotation Yrotation Zrotation\n")
                                
                                tab_writer(i,f)
                                if i == n_bones-1:
                                    f.write("End Site\n")
                                else:
                                    f.write("JOINT Bone.00{}".format(i+1) + "\n")

                                tab_writer(i,f)
                                f.write("{\n")

                                last_point_x, last_point_z = point[0], point[1]
                            else:
                                for j in range(1,n_bones+2):
                                    tab_writer(i-j,f)
                                    f.write("}\n")
                        f.write("MOTION\n")
                        f.write("Frames: \n")         # Esta linea la modificaremos más adelante, cuanto tengamos el conteo de frames
                        f.write("Frame Time: {:.6f}\n".format(1/fps))

                    f.write("{:.6f} ".format(0) + "{:.6f} ".format(0) + "{:.6f} ".format(0))        # XYZposition del primer hueso, en nuestro caso será 0 siempre ya que la base no se mueve
                    for i in range(n_bones):
                        point1, point2 = points[i], points[i+1]
                        delta_y, delta_x = point1[0] - point2[0], point1[1] - point2[1] # La coordenadas estan invertidas en las imagenes
                        rads = np.arctan2(delta_x, delta_y)
                        degrees = np.degrees(rads)
                        rotation = degrees
                        if i > 0:
                            rotation -= last_degrees
                        f.write("{:.6f} ".format(0) + "{:.6f} ".format(rotation) + "{:.6f} ".format(0))          # Rotación en Y
                        last_degrees = degrees         # Para calcular los grados necesitamos la referencia del anterior punto
                    f.write("\n")
                    
                ##############
                ## CILINDRO ##

                # Puntos para calcular la anchura (n_rings)
                last, first = longest_segment[0][0], longest_segment[-1][0]
                step = int(n_pixels/n_rings)
                points_w = []       # Esto es lo que necesita cilindro.py
                for i in range(1,n_rings):
                    points_w.insert(0,longest_segment[step*i][0])
                points_w.append(last)
                points_w.insert(0,first)
                
                if frames == 1:
                    for i in range(0, n_rings+1):
                        y = (first[1] - points_w[i][1]) * escala
                        if write_config_file: f1.write(str(y) + " ")
                    if write_config_file: f1.write("\n")

                for i in range(n_rings+1):
                    if i < n_rings: point1, point2 = points_w[i], points_w[i+1] 
                    else: point1, point2 = points_w[i], points_w[i-1]
                    y_delta = (point2[1] - point1[1])
                    x_delta = (point2[0] - point1[0])
                    m = y_delta / x_delta if x_delta != 0 else np.inf
                    m_perpendicular = -1.0 / m if m != 0 else np.inf
                    x1,y1 = point1

                    x_perpendicular = x1
                    if m != 0: 
                        y_perpendicular = y1 + m_perpendicular  * (x_perpendicular - x1)
                    else:
                        y_perpendicular = y1 + 1
                    while True:
                        if m!= 0:
                            if (int(y_perpendicular) >= np.size(thresh,0)) or (int(x_perpendicular) >= np.size(thresh,1)) or thresh[int(y_perpendicular), int(x_perpendicular)] == 0:
                                x_perpendicular += 1
                                y_perpendicular = y1 + m_perpendicular  * (x_perpendicular - x1)
                                break
                            x_perpendicular -= 1
                            y_perpendicular = y1 + m_perpendicular  * (x_perpendicular - x1)
                        else:
                            if (int(y_perpendicular) >= np.size(thresh,0)) or thresh[int(y_perpendicular), int(x_perpendicular)] == 0:
                                y_perpendicular -= 1
                                break
                            y_perpendicular += 1

                    cv.line(branch, point1, (int(x_perpendicular), int(y_perpendicular)), 255)      # Hacia izquierda o hacia arriba
                    if write_config_file: 
                        l = math.dist(point1, [x_perpendicular, y_perpendicular]) * escala
                        f1.write(str(l) + " ")

                    x_perpendicular = x1
                    if m != 0: 
                        y_perpendicular = y1 + m_perpendicular  * (x_perpendicular - x1)
                    else:
                        y_perpendicular = y1 - 1
                    while True:
                        if m!= 0:
                            if (int(y_perpendicular) >= np.size(thresh,0)) or (int(x_perpendicular) >= np.size(thresh,1)) or thresh[int(y_perpendicular), int(x_perpendicular)] == 0:
                                x_perpendicular -= 1
                                y_perpendicular = y1 + m_perpendicular  * (x_perpendicular - x1)
                                break
                            x_perpendicular += 1
                            y_perpendicular = y1 + m_perpendicular  * (x_perpendicular - x1)
                        else:
                            if (int(y_perpendicular) >= np.size(thresh,0)) or thresh[int(y_perpendicular), int(x_perpendicular)] == 0:
                                y_perpendicular += 1
                                break
                            y_perpendicular -= 1

                    cv.line(branch, point1, (int(x_perpendicular), int(y_perpendicular)), 255)      # Hacia derecha o hacia abajo
                    if write_config_file: 
                        l = math.dist(point1, [x_perpendicular, y_perpendicular]) * escala
                        f1.write(str(l) + " ")
                if write_config_file: 
                        f1.write("\n")    
                
                ############

                flame = gray_frame.copy()
                sk, _ = cv.findContours(branch, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
                cv.drawContours(flame, sk, -1, (0, 0, 255), 1)

                #test = branch

                ##########
                #cv.imwrite("D:\\TFG\\apartado 9\\skeletonize\\test.png", test)
                #cv.imshow('test',test)
                #if frames == 86:
                #    cv.imwrite("D:\\TFG\\MEMORIA\\test\\86.png", frame)
                #    cv.imwrite("D:\\TFG\\MEMORIA\\test\\86_gray.png", flame)
                # if frames == 50:
                #     cv.imwrite("D:\\TFG\\MEMORIA\\test\\50.png", frame)
                #     cv.imwrite("D:\\TFG\\MEMORIA\\test\\50_gray.png", flame)
                # if frames == 90:
                # #     cv.imwrite("D:\\TFG\\MEMORIA\\test\\90_corner.png", pruned_skeleton)
                # #     cv.imwrite("D:\\TFG\\MEMORIA\\test\\90_skel.png", skel_image)
                #     cv.imwrite("D:\\TFG\\MEMORIA\\test\\90.png", frame)
                #     cv.imwrite("D:\\TFG\\MEMORIA\\test\\90_gray.png", flame)
                # if frames == 1:
                #     cv.imwrite("D:\\TFG\\apartado 9\\skeletonize\\flame_skel.png", flame)
                #     cv.imwrite("D:\\TFG\\apartado 9\\skeletonize\\test.png", branch)
                
                ##########

                if view_gray: cv.imshow('gray',gray_frame)
                if view_binary: cv.imshow('thresh',thresh)
                if view_skel_raw: cv.imshow('Skeleton', skel_image)
                if view_skel_treated: cv.imshow('branch', branch)
                if view_flame_skel: cv.imshow('flame_skel',flame)
                if cv.waitKey(5) & 0xFF == ord('q'):
                    break

            video.release()
            cv.destroyAllWindows()

            if write_config_file:
                f1.write(str(temperature))
                f1.close()
            if write_armature_file:
                f.close()

                f = open(bvh_file_path, "r")
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if line.startswith("Frames:"):
                        lines[i] = "Frames: {}".format(frames) + "\n"        # Modificamos esta línea una vez tenemos los frames contados
                f.close()
                f = open(bvh_file_path, "w")
                f.writelines(lines)

    else:
        raise FileNotFoundError("No existe ningún vídeo llamado \"" + flame_video_name + "\"")