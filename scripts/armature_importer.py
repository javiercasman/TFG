import bpy
import os

def import_armature(flame_video_name, collection_name):
    flame_name = flame_video_name.split('.')[0]
    dir = (os.path.abspath(os.path.join(bpy.path.abspath("//"), os.pardir)))
    dir = (os.path.abspath(os.path.join(dir, os.pardir))) #//TFG
    directory =  dir + ("//") + "flames" + ("//") + flame_name
    if not os.path.exists(directory):
        raise FileNotFoundError("No existen los archivos procesados del video \"" + flame_name +"\".")
    bvh_name = "Armature_" + flame_name
    bvh_file_path = directory + ("//") + bvh_name + ".bvh"
    if not os.path.exists(bvh_file_path):
            raise FileNotFoundError("No existe ningun armature llamado \"" + bvh_name + "\".")
    armature_name = "Armature_" + collection_name
    if armature_name not in bpy.context.scene.objects.keys():
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection_name]
        obj = bpy.data.objects["arm_ref_" + collection_name]    #punto de referencia de coordenadas para importar el armature
        bpy.ops.import_anim.bvh(filepath=bvh_file_path,  axis_forward='Y', axis_up='Z')

        armature = bpy.data.objects[bvh_name]
        armature.name = armature_name

        #bpy.context.collections[collection_name].objects.link(armature)

        armature.location = obj.location

        llama = bpy.data.objects["Llama_" + collection_name]

        bpy.ops.object.select_all(action='DESELECT')
        
        llama.select_set(True)
        armature.select_set(True)  

        bpy.context.view_layer.objects.active = llama  # the active object will be the parent of all selected object

        bpy.ops.object.parent_set()

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.ops.object.delete()
        bpy.ops.object.select_all(action='DESELECT')
        #bpy.ops.object.parent_set(type='ARMATURE_AUTO')     # Quitar esto, no queremos que la llama esté bindeada con el armature, queremos que esté bindeada con mesh deform al cilindro, eso se hace en cylindre_generator
       # armature.parent = llama
    #    armature.hide_viewport = True
        armature.hide_render = True
        armature.hide_set(True)
    else:
        print("El armature ya está importado")