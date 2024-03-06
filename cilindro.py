import bpy

armature = bpy.data.objects["armature"]

if armature:
    bones = [armature.pose.bones[i] for i in range(0,6)]
    bbox = [armature.matrix_world @ armature.pose.bones[0].head]
    bbox += ([armature.matrix_world @ b.tail for b in bones])
    min_z = min(bbox, key=lambda v: v.z).z
    max_z = max(bbox, key=lambda v: v.z).z
    
    altura_cilindro = max_z - min_z
    radio_cilindro = 0.2

    bpy.ops.mesh.primitive_cylinder_add(radius=radio_cilindro, depth=altura_cilindro)
    
    cilindro = bpy.context.active_object

    loc = armature.matrix_world @ armature.pose.bones[0].tail
    loc.z += altura_cilindro/2
    cilindro.location = loc
    
    bpy.context.view_layer.objects.active = armature
    
    cilindro.select_set(True)
    armature.select_set(True)

    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    bpy.context.view_layer.objects.active = cilindro
    bpy.context.view_layer.update()

    # Selecciona todos los vértices del cilindro
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    # Divide el cilindro en 12 segmentos horizontales
    bpy.ops.mesh.subdivide(number_cuts=10)

    # Vuelve al modo de objeto
    bpy.ops.object.mode_set(mode='OBJECT')

else:
    print("Armature no encontrado.") 