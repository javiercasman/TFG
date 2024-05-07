import os, sys, bpy
dir = os.path.dirname(bpy.data.filepath)
dir = (os.path.abspath(os.path.join(dir, os.pardir)))
dir = (os.path.abspath(os.path.join(dir, os.pardir))) #dos para atrás
dir = os.path.join(dir, "scripts")
if not dir in sys.path:
     sys.path.append(dir )
from armature_importer import import_armature as import_armature
from animation_setup import animation_setup as animation_setup

#import_armature("flame.mp4", "flame_6_12")
animation_setup("flame.mp4", "flame_6_12")