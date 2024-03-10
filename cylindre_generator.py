import bpy

def generate_cilinder(division_points):
    armature = bpy.data.objects["armature"]

    if armature:
    #    bones = [armature.pose.bones[i] for i in range(0,6)]
    #    bbox = [armature.matrix_world @ armature.pose.bones[0].head]
    #    bbox += ([armature.matrix_world @ b.tail for b in bones])
    #    min_z = min(bbox, key=lambda v: v.z).z
    #    max_z = max(bbox, key=lambda v: v.z).z
        
    #    altura_cilindro = max_z - min_z

        llama = bpy.data.objects["Llama"]
        altura_cilindro = llama.dimensions.z + 0.01
        
    #    radio_cilindro = 0.2
        radio_cilindro = max(llama.dimensions.x, llama.dimensions.y) / 2 + 0.05

        bpy.ops.mesh.primitive_cylinder_add(radius=radio_cilindro, depth=altura_cilindro)
        
        cilindro = bpy.context.active_object

    #    loc = armature.matrix_world @ armature.pose.bones[0].head
    #    loc.z += altura_cilindro/2
        loc = llama.location
        cilindro.location = loc
        bpy.context.view_layer.objects.active = armature

        cilindro.select_set(True)
        armature.select_set(True)

        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        
        bpy.context.view_layer.objects.active = armature

        bpy.context.view_layer.objects.active = cilindro
        bpy.context.view_layer.update()

        # Selecciona todos los vértices del cilindro
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')

        for z in division_points:
             bpy.ops.mesh.bisect(plane_co=(0, 0, z), plane_no=(0, 0, 1), use_fill=True, clear_inner=True, clear_outer=True)

        bpy.ops.object.mode_set(mode='OBJECT')

    else:
        print("Armature no encontrado.") 