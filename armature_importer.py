import bpy
import os

def import_armature(flame_video_name):
    flame_name = flame_video_name.split('.')[0]
    directory =  bpy.path.abspath("//") + "flames" + ("//") + flame_name
    if not os.path.exists(directory):
        raise FileNotFoundError("No existen los archivos procesados del video \"" + flame_name +"\".\nPara solucionarlo, debe activar write_armature_file y/o write_cylinder_config_file")
    armature_name = "Armature_" + flame_name
    bvh_file_path = directory + ("//") + armature_name + ".bvh"
    if not os.path.exists(bvh_file_path):
            raise FileNotFoundError("No existe ningun armature llamado \"" + armature_name + "\".\nPara generarlo, debe activar write_armature_file")
    if armature_name not in bpy.context.scene.objects.keys():
        obj = bpy.data.objects["arm_ref"]    #punto de referencia de coordenadas para importar el armature
        bpy.ops.import_anim.bvh(filepath=bvh_file_path,  axis_forward='Y', axis_up='Z')

        armature = bpy.data.objects[armature_name]

        #bpy.data.collections["Collection"].objects.link(armature)

        armature.location = obj.location

        llama = bpy.data.objects["Llama"]

        llama.select_set(True)
        armature.select_set(True)

        bpy.ops.object.parent_set(type='ARMATURE_AUTO')     # Quitar esto, no queremos que la llama esté bindeada con el armature, queremos que esté bindeada con mesh deform al cilindro, eso se hace en cylindre_generator

    #    armature.hide_viewport = True
        armature.hide_render = True
    else:
        print("El armature ya está importado")