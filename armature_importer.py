import bpy

obj = bpy.data.objects["arm_ref"]    #punto de referencia de coordenadas para importar el armature

bpy.ops.import_anim.bvh(filepath="armature.bvh",  axis_forward='Y', axis_up='Z')

armature = bpy.data.objects["armature"]

#bpy.data.collections["Collection"].objects.link(armature)

armature.location = obj.location


llama = bpy.data.objects["Llama"]

llama.select_set(True)
armature.select_set(True)

bpy.ops.object.parent_set(type='ARMATURE_AUTO')

armature.hide_viewport = True
armature.hide_render = True