bl_info = {
    "name": "New Candle",
    "author": "Javier Castaño",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Adds a new Mesh Object",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}


import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty, StringProperty, BoolProperty, IntProperty
from bpy_extras.object_utils import AddObjectHelper
from mathutils import Vector
import os
import sys
import subprocess

## INSTALL MODULES ##
path = sys.executable
subprocess.call([path, "-m", "ensurepip"])
modules = ["scikit-image", "opencv-python", "plantcv", "colour-science"]
for module in modules:
    subprocess.call([path, "-m", "pip", "install", module])

def find_area(area_type):
    try:
        for a in bpy.data.window_managers[0].windows[0].screen.areas:
            if a.type == area_type:
                return a
        return None
    except:
        return None
    
def camera_param():
    area = find_area("VIEW_3D")
    if area is None:
        print("area not find")
    else:
        r3d = area.spaces[0].region_3d
        location_pivot = r3d.view_location
        view_mat = r3d.perspective_matrix
        direction = view_mat.to_3x3().row[2]
        distance = r3d.view_distance
        distance_vector = distance * direction
        location = location_pivot - distance_vector
        return location, direction
    
def view3d_to_3dcursor():
    area = find_area("VIEW_3D")
    if area is None:
        print("area not find")
    else:
        bpy.ops.view3d.view_center_cursor()

#Scale de 0.64

def duplicate_collection(self, context, col_name): #Duplica la colección activada
    new_col = bpy.data.collections.new(col_name) #crear colección con el mismo nombre (se creará con '.00X')
    context.scene.collection.children.link(new_col)
    src_col = bpy.data.collections[col_name]
    for i,obj in enumerate(src_col.all_objects):
        if i >= 3:
            obj.hide_set(False)
        obj.select_set(True)
    bpy.ops.object.duplicate()
    for i in range(len(context.selected_objects)):
        dup_obj = context.selected_objects[0]
        src_col.objects.unlink(dup_obj)
        new_col.objects.link(dup_obj)
    new_col.objects[3].hide_set(True)
    new_col.objects[4].hide_set(True)
    src_col.objects[3].hide_set(True)
    src_col.objects[4].hide_set(True)
    

def add_candle(self, context, col_name):
    context.view_layer.active_layer_collection = context.view_layer.layer_collection
    file_path = self.main_path + ("//") + "Blender" + ("//") + "espelma.blend"
    inner_path = 'Collection'
    object_name = 'Candle'
    old_set = set(bpy.data.collections[:])
    bpy.ops.wm.append(
        filepath =  os.path.join(file_path, inner_path, object_name),
        directory = os.path.join(file_path, inner_path),
        filename = object_name
    )
    new_col = list(set(bpy.data.collections[:]) - old_set)[0] #para saber exactamente la nueva colección añadida con el append
    new_col.name = col_name #OJO, PUEDE SER col_name + "001" o "002"... para eso, tendremos que return .name
    col_name = new_col.name
    for i, obj in enumerate(new_col.all_objects):
        if i == 0:
            obj.name = "Vela_" + col_name
        elif i == 1:
            obj.name = "Mecha_" + col_name
        elif i == 2:
            obj.name = "Llama_" + col_name
        elif i == 3:
            obj.name = "arm_ref_" + col_name
    #new_location = new_col.all_objects[0].location
    return col_name
    
def transform_flame(self, context, collection_name):
    col = bpy.data.collections.get(collection_name)
    for obj in col.all_objects:
        obj.select_set(True)
    translate_value = context.scene.cursor.location - col.all_objects[0].location
    context.view_layer.objects.active = col.all_objects[0]
    context.scene.tool_settings.transform_pivot_point = 'ACTIVE_ELEMENT'
    #Este resize es para ponerlo a 15cm. Habra que cambiarlo para ponerlo segun los cm
    bpy.ops.transform.resize(value=(0.064, 0.064, 0.064), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=0.52, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
    bpy.ops.transform.translate(value=translate_value, orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, True, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
    
    view3d_to_3dcursor()
    #col.objects[3].hide_set(True) #podemos borrarlo?

class CANDLE_OT_dialog_box(Operator):
    """Open the Add Candle Dialog Box"""
    bl_label = "Set Candle parameters"
    bl_idname = "wm.dialog_box"
    
    video_path: StringProperty(
        name="Video Path",
        subtype='FILE_PATH',
        default="",
        description="Choose a video for your candle"
    )
    n_bones: IntProperty(name = "Bones", default = 6, description="Number of bones for the flame armature")
    n_rings: IntProperty(name = "Cylinder rings", default = 12, description = "Number of rings for the bounding cylinder")
    #flame_height: IntProperty(name = "Candle height (cm)", default = 15, description = "Set the height of the candle in centimeters (5 <= height <= 30)", min = 5, max = 30)
    view_gray: BoolProperty(name = "View gray frames", default = False, description = "Check to display black and white video frames")
    view_binary: BoolProperty(name = "View thresholded frames", default = False, description = "Check to display thresholded video frames")
    view_skel_raw: BoolProperty(name = "View unprocessed skeleton", default = False, description = "Check to display video frames with unprocessed skeleton")
    view_skel_treated: BoolProperty(name = "View processed skeleton", default = False, description = "Check to display video frames with processed skeleton + width lines")
    view_flame_skel: BoolProperty(name = "View gray frame + skeleton", default = False, description = "Check to display black and white video frames with treated skeleton overlaid")

    main_path = ""
    
    def execute(self,context):
        #Si le damos a OK:
        bpy.ops.object.select_all(action = 'DESELECT')
        # dir = os.path.dirname(bpy.data.filepath)
        # dir = (os.path.abspath(os.path.join(dir, os.pardir)))
        # dir = (os.path.abspath(os.path.join(dir, os.pardir))) #dos para atrás
        # dir = os.path.join(dir, "scripts")
        #dir = os.path.dirname(os.path.abspath(__file__))
        dir = context.preferences.filepaths.script_directories.values()[0].directory
        self.main_path = (os.path.abspath(os.path.join(dir, os.pardir)))
        if not dir in sys.path:
            sys.path.append(dir )
        from armature_generator import generate_armature as generate_armature
        from armature_importer import import_armature as import_armature
        from animation_setup import animation_setup as animation_setup

        video_name = (self.video_path.split("//")[-1].split("\\")[-1]) #Nombre del video (con ".mp4")
        video_name_no_format = video_name.split(".")[0] #Nombre del video (sin ".mp4")
        col_name = video_name_no_format + "_" + str(self.n_bones) + "_" + str(self.n_rings) #Ej: "flame_6_12"
        scene_col = bpy.data.collections.get(col_name)
        # mover cursor 3d a x metros adelante en la dirección que mira la cámara
        loc, dir = camera_param()
        context.scene.cursor.location = loc + (dir * Vector((5.0, 5.0, 5.0)))
        if scene_col is None:
            #No existe en la escena, por lo tanto tendremos que importarlo
            new_col_name = add_candle(self,context,col_name) #añadirá la colección con nombre = new_col_name
            generate_armature(video_name, self.n_bones, self.n_rings, self.view_gray, self.view_binary, 
                              self.view_skel_raw, self.view_skel_treated, self.view_flame_skel)
            import_armature(video_name, new_col_name)
            animation_setup(video_name, new_col_name)
            transform_flame(self,context,new_col_name)

            #bpy.ops.object.select_all(action = 'DESELECT')
            #bpy.data.collections.get(new_col_name).objects[3].select_set(True)
            #bpy.ops.object.delete()
            #bpy.ops.object.select_all(action = 'DESELECT')
        else:
            #Existe en la escena
            duplicate_collection(self,context,col_name)
            #Pero tambien tenemos que ver si queremos enseñar los frames
            # Hay que ocultar el cilindro y no se que mas
            if self.view_gray or self.view_binary or self.view_skel_raw or self.view_skel_treated or self.view_flame_skel:
                    generate_armature(video_name, self.n_bones, self.n_rings, self.view_gray, self.view_binary, 
                                      self.view_skel_raw, self.view_skel_treated, self.view_flame_skel)

        return {'FINISHED'}
        
    def invoke(self,context,event):
        return context.window_manager.invoke_props_dialog(self)

class CANDLE_OT_add_candle(Operator, AddObjectHelper):
    """Create a new Candle Mesh"""
    bl_idname = "mesh.add_candle"
    bl_label = "Add Mesh Candle"
    bl_options = {'REGISTER', 'UNDO'}

    scale: FloatVectorProperty(
        name="scale",
        default=(1.0, 1.0, 1.0),
        subtype='TRANSLATION',
        description="scaling",
    )

    def execute(self, context):

        bpy.ops.wm.dialog_box('INVOKE_DEFAULT')

        return {'FINISHED'}


# Registration

def add_candle_button(self, context):
    self.layout.operator(
        CANDLE_OT_add_candle.bl_idname,
        text="Add Candle",
        icon='PLUGIN')


# This allows you to right click on a button and link to documentation
def add_candle_manual_map():
    url_manual_prefix = "https://docs.blender.org/manual/en/latest/"
    url_manual_mapping = (
        ("bpy.ops.mesh.add_candle", "scene_layout/object/types.html"),
    )
    return url_manual_prefix, url_manual_mapping


def register():
    bpy.utils.register_class(CANDLE_OT_add_candle)
    bpy.utils.register_class(CANDLE_OT_dialog_box)
    bpy.utils.register_manual_map(add_candle_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.append(add_candle_button)


def unregister():
    bpy.utils.unregister_class(CANDLE_OT_add_candle)
    bpy.utils.unregister_class(CANDLE_OT_dialog_box)
    bpy.utils.unregister_manual_map(add_candle_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_candle_button)


if __name__ == "__main__":
    register()
