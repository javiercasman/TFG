import numpy as np
from skimage.morphology import skeletonize
from skimage import img_as_ubyte
from skimage.draw import line
from scipy.ndimage import binary_fill_holes
import cv2 as cv
from plantcv import plantcv as pcv
import math
import bpy
from armature_generator import generate_armature as generate_armature
from armature_importer import import_armature as import_armature
from cylindre_generator import generate_cylinder as generate_cylinder

write_file = False          # Depende de si queremos reescribir el .bvh o no
division_points = []

generate_armature(write_file, division_points)
import_armature()
generate_cylinder(division_points)