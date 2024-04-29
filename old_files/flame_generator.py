import bpy
import sys
import os
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir )

from armature_generator import generate_armature as generate_armature
from armature_importer import import_armature as import_armature
from animation_setup import animation_setup as animation_setup

## PARÁMETROS DE armature_generator.py ##

flame_video_name = 'flame.mp4'          # Nombre del vídeo de referencia para el armature.
bones = 6                               # N bones del armature.
width_rings = 12                        # N anillos que tendrá el bounding cylinder.

view_gray = False                       # True para ver los frames de la llama en blanco y negro
view_binary = False                     # True para ver los frames de la llama aplicando el binary threshold
view_skel_raw = False                   # True para ver el skeleton calculado con la imagen binarizado
view_skel_treated = False               # True para ver el skeleton después del proceso de tratamiento aplicado y las líneas perpendiculares calculadas
view_convex_hull = False                # True para ver los frames de la llama binarizada con convex hull aplicado
view_flame_skel = False                 # True para ver la llama en blanco y negro con el skeleton tratado superpuesto en la imagen

#########################################

#   Este código asume que en la escena de Blender ya existe una llama de nombre "Llama" y un punto de referencia para el armature, llamado arm_ref,
#   y crea un armature, un bounding_cylinder para importarlos a la escena, además de modificar ciertos parámetros del objeto de la llama.
try:
    generate_armature(flame_video_name, bones, width_rings - 1, view_gray, 
                    view_binary, view_skel_raw, view_skel_treated, view_convex_hull, view_flame_skel)
    import_armature(flame_video_name)
    animation_setup(flame_video_name)
except Exception as e:
    print(f"Se produjo un error: {e}")